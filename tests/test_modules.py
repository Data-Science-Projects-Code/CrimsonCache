import os
import sys
import pytest
from importlib.util import find_spec

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")


def test_required_modules_exist():
    """Test that all required Python modules exist"""
    required_modules = [
        "donor_generator.py",
        # "generate_donations.py",
        # "generate_daily_activity.py",
    ]

    for module in required_modules:
        module_path = os.path.join(SRC_DIR, module)
        assert os.path.exists(module_path), f"Required module {module} is missing"


def test_modules_can_be_imported():  # Removed SRC_DIR as a parameter
    """Test that all required modules can be imported"""
    # Add src directory to Python path
    sys.path.append(SRC_DIR)

    modules_to_test = [
        "donor_generator",
        # "generate_donations",
        # "generate_daily_activity",
    ]

    for module_name in modules_to_test:
        if find_spec(module_name) is None:
            pytest.fail(f"Failed to find module: {module_name}")
        try:
            __import__(module_name)  # or importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import module {module_name}: {e}")
        except (
            Exception
        ) as e:  # Catch any other exceptions that may happen during import
            pytest.fail(f"Unexpected error during import of {module_name}: {e}")
