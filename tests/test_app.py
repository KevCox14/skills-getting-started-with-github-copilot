import sys
import pytest
from pathlib import Path
from copy import deepcopy
from urllib.parse import quote


# Ensure `src` is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from app import app, activities  # noqa: E402
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def restore_activities():
    original = deepcopy(activities)
    yield
    # restore global in-memory activities to original state
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Debate Team" in data


def test_signup_and_unregister_flow():
    activity = "Debate Team"
    email = "pytest_tester@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    r = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    r = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert r.status_code == 200
    assert email not in activities[activity]["participants"]
