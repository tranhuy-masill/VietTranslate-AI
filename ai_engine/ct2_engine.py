"""Explicit CTranslate2 deployment for the verified SwitchOut V3 checkpoint."""
import hashlib
import json
import os
import time
from pathlib import Path

SOURCE_SHA256 = "2071a5dc03fd9149c4f4d447ab2cd7f612e92e5cf90b503d28fbf48d56cca2cc"
DEFAULT_DIR = Path(__file__).resolve().parent / "saved_model_ct2"


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bundle(path):
    path = Path(path)
    manifest = json.loads((path / "deployment_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("source_sha256") != SOURCE_SHA256 or manifest.get("storage") != "float16":
        raise ValueError("Expected verified SwitchOut V3 float16 bundle.")
    files = manifest.get("files", {})
    required = {"model.bin", "config.json", "tokenizer/source.spm",
                "tokenizer/target.spm", "tokenizer/vocab.json",
                "tokenizer/config.json"}
    if not required.issubset(files):
        raise ValueError("Incomplete CT2 deployment manifest.")
    for name, digest in files.items():
        file = (path / name).resolve()
        if not file.is_relative_to(path.resolve()) or not file.is_file():
            raise ValueError(f"Missing or invalid bundle file: {name}")
        if sha256_file(file) != digest:
            raise ValueError(f"Bundle hash mismatch: {name}")
    return manifest


class CT2TranslationEngine:
    def __init__(self):
        import ctranslate2 as ct2
        from transformers import MarianTokenizer

        path = Path(os.environ.get("VIETTRANSLATE_CT2_DIR", str(DEFAULT_DIR)))
        manifest = validate_bundle(path)
        self.device = os.environ.get("VIETTRANSLATE_CT2_DEVICE", "cuda").lower()
        self.compute_type = os.environ.get("VIETTRANSLATE_CT2_COMPUTE", "float16").lower()
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("CT2 device must be cpu or cuda.")
        if self.device == "cpu" and self.compute_type == "float16":
            raise ValueError("CPU is not the benchmarked CUDA FP16 configuration; set compute type to int8 or float32 explicitly.")
        if self.compute_type not in ct2.get_supported_compute_types(self.device):
            raise RuntimeError(f"Unsupported CT2 compute type {self.compute_type} on {self.device}.")
        self.tokenizer = MarianTokenizer.from_pretrained(str(path / "tokenizer"), local_files_only=True)
        self.model = ct2.Translator(
            str(path), device=self.device, device_index=0,
            compute_type=self.compute_type, inter_threads=1,
        )
        if str(self.model.compute_type) != self.compute_type:
            raise RuntimeError("CT2 selected a different compute type.")
        self.suppress = manifest["suppress_sequences"]
        self.parameters = int(manifest["parameters"])
        self.runtime = "CTranslate2"
        self.checkpoint_sha256 = manifest["source_sha256"]
        self.model_name = "MarianMT SwitchOut p=0.02"

    def translate(self, text, beam_size=4, max_new_tokens=128):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text cannot be empty.")
        if not 1 <= beam_size <= 8:
            raise ValueError("Beam size must be between 1 and 8.")
        if not 1 <= max_new_tokens <= 256:
            raise ValueError("Invalid max_new_tokens.")
        text = text.strip()
        start = time.perf_counter()
        ids = self.tokenizer(text, truncation=False)["input_ids"]
        if len(ids) > 128:
            raise ValueError("Input exceeds 128 tokens. Please split the text into shorter sentences.")
        source = self.tokenizer.convert_ids_to_tokens(ids)
        result = self.model.translate_batch(
            [source], beam_size=beam_size, patience=1.0, length_penalty=1.0,
            no_repeat_ngram_size=0, max_input_length=0,
            max_decoding_length=max_new_tokens, min_decoding_length=0,
            suppress_sequences=self.suppress or None, return_scores=False,
            asynchronous=False, sampling_topk=1,
        )[0]
        output_ids = self.tokenizer.convert_tokens_to_ids(result.hypotheses[0])
        translated = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        return {
            "source_text": text, "translated_text": translated,
            "source_language": "en", "target_language": "vi",
            "model": self.model_name, "beam_size": beam_size,
            "input_tokens": len(ids), "output_tokens": len(output_ids),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            "device": self.device,
        }
