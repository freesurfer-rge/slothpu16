from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def sample_program_dir() -> Path:
    sp_dir = (
        Path(__file__).resolve().parents[4]
        / "python"
        / "packages"
        / "pyslothpu16-emulator"
        / "tests"
        / "sample_programs"
    )
    assert sp_dir.exists(), f"sample_programs not found: {sp_dir}"
    return sp_dir
