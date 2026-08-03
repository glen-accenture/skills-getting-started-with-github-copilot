from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_for_activity_adds_participant_to_the_activity():
    # Arrange
    activity_name = "Chess Club"
    email = f"student-{uuid4().hex}@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = f"duplicate-{uuid4().hex}@example.com"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_the_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = f"student-{uuid4().hex}@example.com"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert unregister_response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_accepts_legacy_path_style_route():
    # Arrange
    activity_name = "Chess Club"
    email = f"legacy-{uuid4().hex}@example.com"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_unregister_participant_returns_404_when_email_is_not_registered():
    # Arrange
    activity_name = "Chess Club"
    email = f"missing-{uuid4().hex}@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
