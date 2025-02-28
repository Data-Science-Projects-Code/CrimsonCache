import pytest
import logging
import sys
from pathlib import Path

# Ensure the main.py module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import main, LOGS_DIR


@pytest.fixture
def mock_generate_functions(monkeypatch):
    def mock_generate_donors(seed, num_donors):
        return True

    def mock_generate_donations(seed, days_of_history):
        return True

    def mock_run_daily_activity():
        return True

    monkeypatch.setattr("main.generate_donors", mock_generate_donors)
    monkeypatch.setattr("main.generate_donations", mock_generate_donations)
    monkeypatch.setattr("main.run_daily_activity", mock_run_daily_activity)


def test_main_with_mocked_functions(mock_generate_functions, caplog):
    with caplog.at_level(logging.INFO):
        assert main() is True

        assert "No donor list found. Generating donors..." in caplog.text
        assert "Donor list generated successfully" in caplog.text
        assert (
            "No donations database found. Generating donations history..."
            in caplog.text
        )
        assert "Donation history generated successfully" in caplog.text
        assert "Running daily activity..." in caplog.text
        assert "Daily activity completed successfully" in caplog.text


def test_logs_dir_exists():
    assert LOGS_DIR.exists() and LOGS_DIR.is_dir()
