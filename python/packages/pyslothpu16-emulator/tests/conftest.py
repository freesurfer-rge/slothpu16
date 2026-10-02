from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def sample_program_dir() -> Path:
    sp_dir = Path(__file__).parent / "sample_programs"
    assert sp_dir.exists(), f"sample_programs not found: {sp_dir}"
    return sp_dir
