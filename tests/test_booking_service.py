from app.services.booking_service import (
    create_booking_state,
    update_booking_state,
    get_missing_fields,
    get_next_booking_question,
)


def test_create_booking_state():
    state = create_booking_state()

    assert state["status"] == "collecting"
    assert state["name"] is None
    assert state["email"] is None
    assert state["interview_date"] is None
    assert state["interview_time"] is None


def test_update_booking_state():
    state = create_booking_state()

    update_booking_state(
        state,
        {
            "name": "Harina Khati",
            "email": "harina@example.com",
        },
    )

    assert state["name"] == "Harina Khati"
    assert state["email"] == "harina@example.com"


def test_get_missing_fields():
    state = create_booking_state()

    update_booking_state(
        state,
        {"name": "Harina Khati"},
    )

    assert get_missing_fields(state) == [
        "email",
        "interview_date",
        "interview_time",
    ]


def test_get_next_booking_question():
    state = create_booking_state()

    update_booking_state(
        state,
        {"name": "Harina Khati"},
    )

    assert get_next_booking_question(state) == (
        "What is your email address?"
    )


def test_no_missing_fields():
    state = create_booking_state()

    update_booking_state(
        state,
        {
            "name": "Harina Khati",
            "email": "harina@example.com",
            "interview_date": "2026-11-20",
            "interview_time": "14:30",
        },
    )

    assert get_missing_fields(state) == []
    assert get_next_booking_question(state) is None


def test_partial_updates_preserve_existing_details():
    state = create_booking_state()

    # First message: candidate provides their name.
    update_booking_state(
        state,
        {"name": "Harina Khati"},
    )

    # Second message: candidate provides their email.
    update_booking_state(
        state,
        {
            "email": "harina@example.com",
            "name": None,
        },
    )

    assert state["name"] == "Harina Khati"
    assert state["email"] == "harina@example.com"

    # Third message: candidate provides their preferred date.
    update_booking_state(
        state,
        {"interview_date": "2026-11-20"},
    )

    assert state["name"] == "Harina Khati"
    assert state["email"] == "harina@example.com"
    assert state["interview_date"] == "2026-11-20"

    assert get_missing_fields(state) == ["interview_time"]