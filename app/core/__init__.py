"""Core application configuration and security modules."""

import importlib.util
import os
import sys

# Re-export functions from app/core.py
_core_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core.py")
if os.path.exists(_core_file):
    _spec = importlib.util.spec_from_file_location("app._core_legacy", _core_file)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    say_hello = getattr(_mod, "say_hello", None)
