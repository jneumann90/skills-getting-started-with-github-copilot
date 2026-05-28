import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    email = activities["Programming Class"]["participants"][0]
    response = client.delete("/activities/Programming Class/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Programming Class"
    assert email not in activities["Programming Class"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    email = "notregistered@mergington.edu"
    response = client.delete("/activities/Programming Class/participants", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up"
