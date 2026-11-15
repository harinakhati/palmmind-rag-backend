BOOKING_FIELDS = (
    "name",
    "email",
    "interview_date",
    "interview_time",
)

FIELD_QUESTIONS = {
    "name": "May I have your full name?",
    "email": "What is your email address?",
    "interview_date": "What date would you prefer for the interview?",
    "interview_time": "What time would you prefer for the interview?",
}


def create_booking_state() -> dict:
    """Initialize a new interview booking."""

    return {
        "status": "collecting",
        "name": None,
        "email": None,
        "interview_date": None,
        "interview_time": None,
    }


def update_booking_state(
    booking_state: dict,
    new_details: dict,
) -> dict:
    """Update booking information with newly collected details."""

    for field in BOOKING_FIELDS:
        value = new_details.get(field)

        if value is not None and str(value).strip():
            booking_state[field] = str(value).strip()

    return booking_state


def get_missing_fields(booking_state: dict) -> list[str]:
    """Return booking fields that have not been collected."""

    return [
        field
        for field in BOOKING_FIELDS
        if not booking_state.get(field)
    ]


def get_next_booking_question(booking_state: dict) -> str | None:
    """Return a question for the next missing booking detail."""

    missing_fields = get_missing_fields(booking_state)

    if not missing_fields:
        return None

    next_field = missing_fields[0]

    return FIELD_QUESTIONS[next_field]

def create_booking_summary(booking_state: dict) -> str:
    """Create a summary of the collected interview details."""

    return (
        "Please review your interview booking details:\n\n"
        f"Name: {booking_state['name']}\n"
        f"Email: {booking_state['email']}\n"
        f"Interview Date: {booking_state['interview_date']}\n"
        f"Interview Time: {booking_state['interview_time']}\n\n"
        "Would you like to confirm this booking?"
    )

def set_booking_confirmation(
    booking_state: dict,
    confirmed: bool,
) -> dict:
    """Update booking state after an explicit candidate response."""

    if booking_state.get("status") != "awaiting_confirmation":
        raise ValueError(
            "Booking is not waiting for confirmation."
        )

    if confirmed:
        booking_state["status"] = "confirmed"
    else:
        booking_state["status"] = "cancelled"

    return booking_state


def mark_awaiting_confirmation(booking_state: dict) -> dict:
    """Mark a complete booking as awaiting candidate confirmation."""

    if get_missing_fields(booking_state):
        raise ValueError(
            "Cannot request confirmation while booking details are incomplete."
        )

    booking_state["status"] = "awaiting_confirmation"

    return booking_state
def interpret_confirmation(message: str) -> bool | None:
    """Interpret a user's booking confirmation response."""

    normalized_message = message.strip().lower().rstrip(".!?").strip()

    confirmation_phrases = {
        "yes",
        "yeah",
        "yep",
        "confirm",
        "confirm booking",
        "i confirm",
        "i confirm my booking",
        "i confirm my interview booking",
        "yes, confirm",
        "yes, i confirm",
        "yes, i confirm my booking",
        "yes, i confirm my interview booking",
        "correct",
        "looks good",
        "book it",
    }

    cancellation_phrases = {
        "no",
        "no, cancel",
        "cancel",
        "cancel booking",
        "don't confirm",
        "do not confirm",
        "not now",
    }

    if normalized_message in confirmation_phrases:
        return True

    if normalized_message in cancellation_phrases:
        return False

    return None