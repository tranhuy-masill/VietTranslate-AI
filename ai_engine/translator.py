
import os
import time
import torch

from ai_engine.model_loader import load_model


class HFTranslationEngine:

    def __init__(self):

        self.tokenizer, self.model, self.device = load_model()

        self.model_name = "MarianMT SwitchOut p=0.02"
        self.runtime = "Hugging Face"
        self.compute_type = str(next(self.model.parameters()).dtype).replace("torch.", "")
        self.parameters = sum(p.numel() for p in self.model.parameters())
        self.checkpoint_sha256 = None


    def translate(
        self,
        text: str,
        beam_size: int = 4,
        max_new_tokens: int = 128
    ) -> dict:

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text cannot be empty.")

        if not 1 <= beam_size <= 8:
            raise ValueError("Beam size must be between 1 and 8.")

        if not 1 <= max_new_tokens <= 256:
            raise ValueError("Invalid max_new_tokens.")

        text = text.strip()

        start_time = time.perf_counter()

        # Step 1: Tokenization
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=False
        )

        input_tokens = inputs["input_ids"].shape[1]

        if input_tokens > 128:
            raise ValueError(
                "Input exceeds 128 tokens. "
                "Please split the text into shorter sentences."
            )

        inputs = inputs.to(self.device)

        # Step 2: Translation
        generation_options = {
            "num_beams": beam_size,
            "max_new_tokens": max_new_tokens
        }

        if beam_size > 1:
            generation_options["early_stopping"] = True

        with torch.inference_mode():

            outputs = self.model.generate(
                **inputs,
                **generation_options
            )

        # Step 3: Decoding
        translated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        latency = (
            time.perf_counter() - start_time
        ) * 1000

        # Step 4: Return result
        return {
            "source_text": text,
            "translated_text": translated_text,
            "source_language": "en",
            "target_language": "vi",
            "model": self.model_name,
            "beam_size": beam_size,
            "input_tokens": input_tokens,
            "output_tokens": int(outputs.shape[1]),
            "latency_ms": round(latency, 2),
            "device": str(self.device)
        }


class TranslationEngine:
    """Keep the old HF path unless CT2 is explicitly requested."""
    def __new__(cls):
        runtime = os.environ.get("VIETTRANSLATE_RUNTIME", "hf").lower()
        if runtime == "hf":
            return HFTranslationEngine()
        if runtime == "ct2":
            from ai_engine.ct2_engine import CT2TranslationEngine
            return CT2TranslationEngine()
        raise ValueError("VIETTRANSLATE_RUNTIME must be hf or ct2.")
