
from threading import Lock

from ai_engine.translator import TranslationEngine


class TranslationService:

    def __init__(self):

        self.engine = TranslationEngine()
        self.lock = Lock()

    def translate(
        self,
        text: str,
        beam_size: int = 4,
        max_new_tokens: int = 128
    ):

        with self.lock:

            return self.engine.translate(
                text=text,
                beam_size=beam_size,
                max_new_tokens=max_new_tokens
            )

    def get_model_info(self):

        return {
            "name": "MarianMT",
            "base_model": "Helsinki-NLP/opus-mt-en-vi",
            "method": "SwitchOut",
            "switchout_probability": 0.02,
            "parameters": sum(
                p.numel()
                for p in self.engine.model.parameters()
            ),
            "source_language": "English",
            "target_language": "Vietnamese",
            "device": str(self.engine.device),
            "max_input_tokens": 128,
            "default_beam_size": 4,
            "status": "ready"
        }
