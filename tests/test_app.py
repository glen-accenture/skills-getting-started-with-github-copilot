from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_the_email_from_activity():
    activity_name = "Chess Club"
    email = f"student-{uuid4().hex}@example.com"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert unregister_response.status_code == 200

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_accepts_legacy_path_style_route():
    activity_name = "Chess Club"
    email = f"legacy-{uuid4().hex}@example.com"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_unregister_participant_returns_404_when_email_is_not_registered():
    activity_name = "Chess Club"
    email = f"missing-{uuid4().hex}@example.com"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
