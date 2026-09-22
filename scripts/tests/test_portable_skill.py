"""Include the self-contained portable package tests in the repository suite."""
import importlib.util
import sys
from pathlib import Path


def load_tests(loader, tests, pattern):
    source = Path(__file__).resolve().parents[2] / "Skill/skill-lifecycle/tests/test_bundle.py"
    spec = importlib.util.spec_from_file_location("portable_skill_tests", source)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return loader.loadTestsFromModule(module)
