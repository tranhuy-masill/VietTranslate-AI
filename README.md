# VietTranslate-AI
English–Vietnamese translation with MarianMT SwitchOut.

## Optional optimized runtime (CT2)

The existing Hugging Face backend remains the default. To reproduce the selected GPU configuration, use the exact SwitchOut p=0.02 one-epoch Version 3 best_checkpoint. No training is required. Do not commit model files.

From the repository root, using the backend's existing Python environment:

    python -m pip install -r backend/requirements-ct2.txt
    python -m ai_engine.prepare_ct2 --source ai_engine/saved_model

The converter checks the source model.safetensors SHA-256 against the benchmarked checkpoint, preserves the tokenizer and decoding suppression rules, and creates ai_engine/saved_model_ct2 with a hash manifest. It refuses to overwrite an existing bundle. For a different local checkpoint location pass its directory to --source. Conversion requires a Transformers version compatible with CT2 4.6.0; the research benchmark used Transformers 4.48.3. If needed, convert in a separate Python environment with that version, sentencepiece, sacremoses, torch, safetensors and ctranslate2==4.6.0 installed, then copy the entire verified bundle.

PowerShell (GPU with compatible CUDA 12/cuBLAS and cuDNN libraries for CT2 4.6.0):

    $env:VIETTRANSLATE_RUNTIME = "ct2"
    $env:VIETTRANSLATE_CT2_DEVICE = "cuda"
    $env:VIETTRANSLATE_CT2_COMPUTE = "float16"
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

Bash:

    VIETTRANSLATE_RUNTIME=ct2 VIETTRANSLATE_CT2_DEVICE=cuda VIETTRANSLATE_CT2_COMPUTE=float16 python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

For CPU-only deployment explicitly set device=cpu and compute=int8 (or float32). CPU quality/speed must be measured separately; this is NOT the Tesla T4 FP16 configuration. If CT2 cannot initialize, startup fails rather than silently switching runtime. Set VIETTRANSLATE_RUNTIME=hf to return to the original backend.

Check http://127.0.0.1:8000/api/model for runtime, compute type, device and source checkpoint SHA-256. Test /api/translate and /api/documents/translate via /docs. The text API keeps the existing default beam 4 and max_new_tokens 128; document translation keeps its existing max_new_tokens 256 per chunk. Document speed/quality is not the model benchmark and must be evaluated separately. Existing frontend and endpoint schemas remain compatible.

CPU-only mock contract tests:

    python -m unittest tests.test_ct2_engine

The tests do not verify real model outputs or GPU compatibility. Real checkpoint conversion, API smoke tests and end-to-end measurements are required before merging/deployment.
