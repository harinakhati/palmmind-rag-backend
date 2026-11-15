import json

from app.services.booking_conversation import process_booking_message


class FakeRedis:
    """A simple in-memory Redis substitute for testing."""

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ex=None):
        self.data[key] = value

    def delete(self, key):
        self.data.pop(key, None)


def test_booking_conversation_collects_missing_fields(monkeypatch):
    redis_client = FakeRedis()

    # Mock Gemini extraction.
    def mock_extract_booking_details(message):
        return {
            "name": "Test Candidate",
            "email": None,
            "interview_date": None,
            "interview_time": None,
            "_validation_errors": {},
        }

    monkeypatch.setattr(
        "app.services.booking_conversation.extract_booking_details",
        mock_extract_booking_details,
    )

    result = process_booking_message(
        redis_client,
        "test-conversation-1",
        "My name is Test Candidate.",
    )

    assert result["status"] == "collecting"
    assert result["booking_details"]["name"] == "Test Candidate"
    assert result["missing_fields"] == [
        "email",
        "interview_date",
        "interview_time",
    ]


def test_booking_conversation_handles_invalid_email(monkeypatch):
    redis_client = FakeRedis()

    def mock_extract_booking_details(message):
        return {
            "name": "Test Candidate",
            "email": None,
            "interview_date": None,
            "interview_time": None,
            "_validation_errors": {
                "email": "Please provide a valid email address."
            },
        }

    monkeypatch.setattr(
        "app.services.booking_conversation.extract_booking_details",
        mock_extract_booking_details,
    )

    result = process_booking_message(
        redis_client,
        "test-conversation-2",
        "My name is Test Candidate and my email is invalid.",
    )

    assert result["status"] == "collecting"
    assert result["booking_details"]["name"] == "Test Candidate"
    assert result["booking_details"]["email"] is None
    assert "valid email address" in result["response"]
    assert "email" in result["missing_fields"]


def test_booking_conversation_awaits_confirmation(monkeypatch):
    redis_client = FakeRedis()

    def mock_extract_booking_details(message):
        return {
            "name": "Test Candidate",
            "email": "test@example.com",
            "interview_date": "2026-11-25",
            "interview_time": "11:30:00",
            "_validation_errors": {},
        }

    monkeypatch.setattr(
        "app.services.booking_conversation.extract_booking_details",
        mock_extract_booking_details,
    )

    result = process_booking_message(
        redis_client,
        "test-conversation-3",
        "Here are my interview details.",
    )

    assert result["status"] == "awaiting_confirmation"
    assert result["missing_fields"] == []
    assert "Would you like to confirm" in result["response"]


from unittest.mock import Mock

from app.services.booking_conversation import (
    process_booking_confirmation,
)


def create_awaiting_booking():
    return {
        "status": "awaiting_confirmation",
        "name": "Test Candidate",
        "email": "test@example.com",
        "interview_date": "2026-11-25",
        "interview_time": "11:30:00",
    }


def test_successful_booking_confirmation(monkeypatch):
    redis_client = FakeRedis()
    conversation_id = "confirmation-test"

    redis_client.set(
        f"booking:{conversation_id}",
        json.dumps(create_awaiting_booking()),
    )

    mock_booking = Mock()
    mock_booking.booking_id = "test-booking-id"

    mock_save_booking = Mock(return_value=mock_booking)

    monkeypatch.setattr(
        "app.services.booking_conversation.save_booking",
        mock_save_booking,
    )

    result = process_booking_confirmation(
        redis_client,
        Mock(),
        conversation_id,
        "Yes",
    )

    assert result["status"] == "confirmed"
    assert result["booking_id"] == "test-booking-id"
    mock_save_booking.assert_called_once()
    assert redis_client.get(f"booking:{conversation_id}") is None


def test_booking_cancellation(monkeypatch):
    redis_client = FakeRedis()
    conversation_id = "cancellation-test"

    redis_client.set(
        f"booking:{conversation_id}",
        json.dumps(create_awaiting_booking()),
    )

    mock_save_booking = Mock()

    monkeypatch.setattr(
        "app.services.booking_conversation.save_booking",
        mock_save_booking,
    )

    result = process_booking_confirmation(
        redis_client,
        Mock(),
        conversation_id,
        "Cancel",
    )

    assert result["status"] == "cancelled"
    mock_save_booking.assert_not_called()
    assert redis_client.get(f"booking:{conversation_id}") is None


def test_unclear_confirmation_keeps_booking_pending():
    redis_client = FakeRedis()
    conversation_id = "unclear-confirmation-test"

    redis_client.set(
        f"booking:{conversation_id}",
        json.dumps(create_awaiting_booking()),
    )

    result = process_booking_confirmation(
        redis_client,
        Mock(),
        conversation_id,
        "Maybe later",
    )

    assert result["status"] == "awaiting_confirmation"
    assert redis_client.get(f"booking:{conversation_id}") is not None


def test_confirmation_without_active_booking():
    redis_client = FakeRedis()

    try:
        process_booking_confirmation(
            redis_client,
            Mock(),
            "missing-booking",
            "Yes",
        )
    except ValueError as error:
        assert str(error) == "No active booking found."
    else:
        assert False, "Expected ValueError for missing booking."