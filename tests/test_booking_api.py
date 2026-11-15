from fastapi.testclient import TestClient

from app.main import app
from app.api import booking_routes
from unittest.mock import Mock
from app.database import get_db

def test_booking_chat_endpoint(monkeypatch):
    # Mock the booking conversation service.
    def mock_process_booking_message(
        redis_client,
        conversation_id,
        message,
    ):
        return {
            "conversation_id": conversation_id,
            "status": "collecting",
            "response": "What is your email address?",
            "missing_fields": [
                "email",
                "interview_date",
                "interview_time",
            ],
            "booking_details": {
                "status": "collecting",
                "name": "Test Candidate",
                "email": None,
                "interview_date": None,
                "interview_time": None,
            },
        }

    monkeypatch.setattr(
        booking_routes,
        "process_booking_message",
        mock_process_booking_message,
    )

    with TestClient(app) as client:
        response = client.post(
            "/booking/chat",
            json={
                "message": "My name is Test Candidate."
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "collecting"
    assert data["booking_details"]["name"] == "Test Candidate"
    assert "email" in data["missing_fields"]
    assert data["conversation_id"]


def test_booking_chat_with_existing_conversation_id(monkeypatch):
    expected_id = "existing-conversation-123"

    def mock_process_booking_message(
        redis_client,
        conversation_id,
        message,
    ):
        assert conversation_id == expected_id

        return {
            "conversation_id": conversation_id,
            "status": "collecting",
            "response": "What date would you prefer?",
            "missing_fields": ["interview_date"],
            "booking_details": {
                "status": "collecting",
                "name": "Test Candidate",
                "email": "test@example.com",
                "interview_date": None,
                "interview_time": None,
            },
        }

    monkeypatch.setattr(
        booking_routes,
        "process_booking_message",
        mock_process_booking_message,
    )

    with TestClient(app) as client:
        response = client.post(
            "/booking/chat",
            json={
                "conversation_id": expected_id,
                "message": "My email is test@example.com.",
            },
        )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == expected_id


def test_booking_chat_rejects_empty_message():
    with TestClient(app) as client:
        response = client.post(
            "/booking/chat",
            json={
                "message": "   "
            },
        )

    assert response.status_code == 422


def test_booking_confirmation_endpoint(monkeypatch):
    def mock_process_confirmation(
        redis_client,
        db,
        conversation_id,
        message,
    ):
        assert conversation_id == "test-conversation"
        assert message == "Yes"

        return {
            "conversation_id": conversation_id,
            "status": "confirmed",
            "response": "Your interview booking has been confirmed successfully.",
            "booking_id": "test-booking-id",
        }

    monkeypatch.setattr(
        booking_routes,
        "process_booking_confirmation",
        mock_process_confirmation,
    )

    app.dependency_overrides[get_db] = lambda: Mock()

    try:
        with TestClient(app) as client:
            response = client.post(
                "/booking/confirm",
                json={
                    "conversation_id": "test-conversation",
                    "message": "Yes",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert response.json()["booking_id"] == "test-booking-id"


def test_booking_cancellation_endpoint(monkeypatch):
    def mock_process_confirmation(
        redis_client,
        db,
        conversation_id,
        message,
    ):
        return {
            "conversation_id": conversation_id,
            "status": "cancelled",
            "response": "Your interview booking has been cancelled.",
        }

    monkeypatch.setattr(
        booking_routes,
        "process_booking_confirmation",
        mock_process_confirmation,
    )

    app.dependency_overrides[get_db] = lambda: Mock()

    try:
        with TestClient(app) as client:
            response = client.post(
                "/booking/confirm",
                json={
                    "conversation_id": "test-conversation",
                    "message": "Cancel",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_booking_confirmation_rejects_empty_fields():
    with TestClient(app) as client:
        response = client.post(
            "/booking/confirm",
            json={
                "conversation_id": "   ",
                "message": "Yes",
            },
        )

    assert response.status_code == 422