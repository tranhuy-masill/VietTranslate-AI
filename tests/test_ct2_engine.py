"""CPU-only contract tests; no checkpoint or CTranslate2 library required."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from ai_engine.ct2_engine import CT2TranslationEngine, SOURCE_SHA256, sha256_file, validate_bundle


class CT2ContractTest(unittest.TestCase):
    def test_bundle_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ["model.bin", "config.json", "tokenizer/source.spm",
                     "tokenizer/target.spm", "tokenizer/vocab.json", "tokenizer/config.json"]
            for name in names:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(name.encode())
            manifest = {"source_sha256": SOURCE_SHA256, "storage": "float16",
                        "files": {name: sha256_file(root / name) for name in names}}
            (root / "deployment_manifest.json").write_text(json.dumps(manifest))
            self.assertEqual(validate_bundle(root), manifest)
            (root / "model.bin").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                validate_bundle(root)

    def test_translate_contract_and_limits(self):
        engine = CT2TranslationEngine.__new__(CT2TranslationEngine)
        class FakeTokenizer:
            def __call__(self, text, **kwargs):
                return {"input_ids": [1] * len(text.split())}
            def convert_ids_to_tokens(self, ids):
                return ["token"] * len(ids)
            def convert_tokens_to_ids(self, tokens):
                return [2] * len(tokens)
            def decode(self, ids, **kwargs):
                return "Xin chào"
        class FakeModel:
            def translate_batch(self, source, **kwargs):
                self.options = kwargs
                return [SimpleNamespace(hypotheses=[["token"]])]
        engine.tokenizer = FakeTokenizer()
        engine.model = FakeModel()
        engine.suppress = []
        engine.model_name = "MarianMT SwitchOut p=0.02"
        engine.device = "cuda"
        result = engine.translate("Hello world")
        self.assertEqual(result["translated_text"], "Xin chào")
        self.assertEqual(result["beam_size"], 4)
        self.assertEqual(engine.model.options["max_decoding_length"], 128)
        self.assertEqual(engine.model.options["beam_size"], 4)
        with self.assertRaises(ValueError):
            engine.translate("word " * 129)
        with self.assertRaises(ValueError):
            engine.translate("hello", beam_size=9)


if __name__ == "__main__":
    unittest.main()
