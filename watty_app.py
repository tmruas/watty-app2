"""Compatibilidade com `streamlit run watty_app.py` — executa o mesmo código que `app.py`."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "watty_app_main", Path(__file__).resolve().parent / "app.py"
)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
