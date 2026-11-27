"""Convert the exact evaluated HF V3 checkpoint into a local deployment bundle."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from ai_engine.ct2_engine import DEFAULT_DIR, SOURCE_SHA256, sha256_file, validate_bundle


def prepare(source, output):
    import ctranslate2 as ct2
    from transformers import AutoConfig, GenerationConfig, MarianMTModel, MarianTokenizer

    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    if sha256_file(source / "model.safetensors") != SOURCE_SHA256:
        raise ValueError("Wrong checkpoint: expected SwitchOut p=0.02, one epoch, Version 3.")
    if AutoConfig.from_pretrained(str(source), local_files_only=True).model_type != "marian":
        raise ValueError("Expected MarianMT checkpoint.")
    tokenizer = MarianTokenizer.from_pretrained(str(source), local_files_only=True)
    try:
        gen = GenerationConfig.from_pretrained(str(source), local_files_only=True)
    except OSError:
        gen = GenerationConfig.from_model_config(AutoConfig.from_pretrained(str(source), local_files_only=True))
    original = [tokenizer.convert_ids_to_tokens(ids) for ids in (gen.bad_words_ids or [])]
    original += [[tokenizer.convert_ids_to_tokens(i)] for i in (gen.suppress_tokens or [])]
    suppress = [seq for seq in original if seq and tokenizer.pad_token not in seq
                and "<pad>" not in seq and seq != [tokenizer.eos_token]]
    model = MarianMTModel.from_pretrained(str(source), local_files_only=True)
    parameters = sum(p.numel() for p in model.parameters())
    del model
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ct2-build-", dir=output.parent) as work:
        bundle = Path(work) / "bundle"
        ct2.converters.TransformersConverter(str(source)).convert(str(bundle), quantization="float16", force=False)
        tokdir = bundle / "tokenizer"
        tokdir.mkdir()
        for name in ("source.spm", "target.spm", "vocab.json", "config.json",
                     "tokenizer_config.json", "special_tokens_map.json", "generation_config.json",
                     "added_tokens.json"):
            if (source / name).is_file():
                shutil.copy2(source / name, tokdir / name)
        manifest = {
            "source_sha256": SOURCE_SHA256, "storage": "float16",
            "parameters": parameters, "suppress_sequences": suppress,
            "converter_version": ct2.__version__,
            "files": {p.relative_to(bundle).as_posix(): sha256_file(p)
                      for p in sorted(bundle.rglob("*")) if p.is_file()},
        }
        (bundle / "deployment_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        validate_bundle(bundle)
        bundle.rename(output)
    print(f"Verified deployment bundle: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", default=DEFAULT_DIR, type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
