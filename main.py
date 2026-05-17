"""ASGI entrypoint proxy.

This lets `uvicorn main:app` work from the repository root by loading the
actual FastAPI app from `back-end/main.py`.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


BACKEND_MAIN = Path(__file__).resolve().parent / "back-end" / "main.py"

spec = spec_from_file_location("cohr_backend_main", BACKEND_MAIN)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load backend app from {BACKEND_MAIN}")

module = module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
