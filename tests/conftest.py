"""Load the harness modules by path.

Neither `build/` nor `evals/runners/` is an importable package -- both are
deliberately plain stdlib scripts run with `python3 <path>`, so the tests load
them the same way the repo runs them rather than adding packaging the project
does not otherwise need.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def assemble():
    return _load("assemble_under_test", "build/assemble.py")


@pytest.fixture(scope="session")
def package():
    return _load("package_under_test", "build/package.py")


@pytest.fixture(scope="session")
def aggregate():
    return _load("aggregate_under_test", "evals/runners/aggregate.py")


@pytest.fixture(scope="session")
def judge():
    return _load("judge_under_test", "evals/runners/judge.py")


@pytest.fixture(scope="session")
def report():
    return _load("report_under_test", "evals/runners/report.py")


@pytest.fixture(scope="session")
def redact():
    return _load("redact_under_test", "evals/runners/redact_transcripts.py")
