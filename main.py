"""ASGI entrypoint proxy.

This lets `uvicorn main:app` work from the repository root by loading the
actual FastAPI app from `back-end/main.py`.
"""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent / "back-end"
BACKEND_MAIN = BACKEND_DIR / "main.py"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

spec = spec_from_file_location("cohr_backend_main", BACKEND_MAIN)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load backend app from {BACKEND_MAIN}")

module = module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
