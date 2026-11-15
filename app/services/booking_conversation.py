from app.services.booking_service import (
    create_booking_state,
    update_booking_state,
    get_missing_fields,
    get_next_booking_question,
    mark_awaiting_confirmation,
    create_booking_summary,
    interpret_confirmation,
    set_booking_confirmation,
)

from app.services.redis_service import (
    get_booking_state,
    save_booking_state,
)

from app.services.llm import extract_booking_details
from app.services.redis_service import clear_booking_state
from app.services.booking_repository import save_booking

def process_booking_message(
    redis_client,
    conversation_id: str,
    message: str,
) -> dict:
    """Process a candidate message and update their booking conversation."""

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    # Retrieve existing booking state from Redis.
    booking_state = get_booking_state(
        redis_client,
        conversation_id,
    )

    # Initialize booking state for a new conversation.
    if not booking_state:
        booking_state = create_booking_state()

    # Extract booking details using Gemini.
    extracted_details = extract_booking_details(message)

    # Separate validation errors from extracted booking details.
    validation_errors = extracted_details.pop(
        "_validation_errors",
        {},
    )

    # Clear fields containing invalid information.
    for field in validation_errors:
        booking_state[field] = None

    # Merge valid extracted details with existing information.
    update_booking_state(
        booking_state,
        extracted_details,
    )

    # Handle invalid fields before continuing the conversation.
    if validation_errors:
        field = next(iter(validation_errors))

        validation_questions = {
            "name": "That name doesn't look valid. Please provide your full name.",
            "email": "That email address doesn't look valid. Could you please provide a valid email address?",
            "interview_date": "That interview date is invalid or in the past. Please provide a valid future date.",
            "interview_time": "That interview time is invalid. Please provide a valid time.",
        }

        response = validation_questions[field]

        missing_fields = get_missing_fields(booking_state)

        save_booking_state(
            redis_client,
            conversation_id,
            booking_state,
        )

        return {
            "conversation_id": conversation_id,
            "status": "collecting",
            "response": response,
            "missing_fields": missing_fields,
            "booking_details": booking_state,
        }

    # Check whether any required details are missing.
    missing_fields = get_missing_fields(booking_state)

    if missing_fields:
        response = get_next_booking_question(booking_state)

    else:
        mark_awaiting_confirmation(booking_state)
        response = create_booking_summary(booking_state)

    # Save the updated state in Redis.
    save_booking_state(
        redis_client,
        conversation_id,
        booking_state,
    )

    return {
        "conversation_id": conversation_id,
        "status": booking_state["status"],
        "response": response,
        "missing_fields": missing_fields,
        "booking_details": booking_state,
    }

def process_booking_confirmation(
    redis_client,
    db,
    conversation_id: str,
    message: str,
) -> dict:
    """Handle confirmation or cancellation of an interview booking."""

    booking_state = get_booking_state(
        redis_client,
        conversation_id,
    )

    if not booking_state:
        raise ValueError("No active booking found.")

    if booking_state.get("status") != "awaiting_confirmation":
        raise ValueError("Booking is not waiting for confirmation.")

    confirmation = interpret_confirmation(message)

    if confirmation is None:
        return {
            "conversation_id": conversation_id,
            "status": "awaiting_confirmation",
            "response": (
                "I couldn't understand your response. "
                "Please reply with 'yes' to confirm or 'cancel' to cancel."
            ),
        }

    set_booking_confirmation(
        booking_state,
        confirmation,
    )

    if confirmation:
        booking = save_booking(db, booking_state)

        clear_booking_state(
            redis_client,
            conversation_id,
        )

        return {
            "conversation_id": conversation_id,
            "status": "confirmed",
            "response": (
                "Your interview booking has been confirmed successfully."
            ),
            "booking_id": booking.booking_id,
        }

    clear_booking_state(
        redis_client,
        conversation_id,
    )

    return {
        "conversation_id": conversation_id,
        "status": "cancelled",
        "response": "Your interview booking has been cancelled.",
    }
