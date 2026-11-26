
import time
import torch

from pathlib import Path
from functools import lru_cache
from transformers import MarianMTModel, MarianTokenizer


MODEL_DIR = Path(__file__).resolve().parent / "saved_model"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


@lru_cache(maxsize=1)
def load_model():

    print("=" * 50)
    print("Loading MarianMT Translation Model")
    print("=" * 50)

    if not MODEL_DIR.is_dir():
        raise FileNotFoundError(
            f"Model directory not found: {MODEL_DIR}"
        )

    start_time = time.perf_counter()

    tokenizer = MarianTokenizer.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True
    )

    model = MarianMTModel.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True
    )

    model = model.to(DEVICE)
    model.eval()

    load_time = time.perf_counter() - start_time

    parameters = sum(
        p.numel() for p in model.parameters()
    )

    print(f"Model directory: {MODEL_DIR}")
    print(f"Device: {DEVICE}")
    print(f"Parameters: {parameters:,}")
    print(f"Loading time: {load_time:.2f}s")
    print("Model loaded successfully!")

    return tokenizer, model, DEVICE


if __name__ == "__main__":
    load_model()
