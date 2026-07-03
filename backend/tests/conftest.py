"""
Shared pytest fixtures for all test files.
"""

import copy
import os
import sys

import pytest

# Make sure the backend folder (one level up) is importable
# no matter where pytest is run from.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import database  # noqa: E402  (import after sys.path tweak on purpose)
from app import app as flask_app  # noqa: E402

# Keep an untouched copy of the starting data so every test
# begins with the same inventory.
ORIGINAL_INVENTORY = copy.deepcopy(database.inventory)


@pytest.fixture(autouse=True)
def fresh_database():
    """Reset the mock database before every single test."""
    database.inventory.clear()
    database.inventory.extend(copy.deepcopy(ORIGINAL_INVENTORY))
    yield


@pytest.fixture
def client():
    """A Flask test client for making fake HTTP requests."""
    flask_app.config["TESTING"] = True
    return flask_app.test_client()
