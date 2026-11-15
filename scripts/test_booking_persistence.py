from app.database import SessionLocal
from app.services.booking_service import (
    create_booking_state,
    update_booking_state,
    mark_awaiting_confirmation,
    set_booking_confirmation,
)
from app.services.booking_repository import save_booking


db = SessionLocal()

try:
    state = create_booking_state()

    update_booking_state(
        state,
        {
            "name": "Test Candidate",
            "email": "testcandidate@example.com",
            "interview_date": "2026-11-20",
            "interview_time": "14:30",
        },
    )

    mark_awaiting_confirmation(state)
    set_booking_confirmation(state, True)

    booking = save_booking(db, state)

    print("Booking saved successfully!")
    print("Booking ID:", booking.booking_id)
    print("Name:", booking.name)
    print("Email:", booking.email)
    print("Interview Date:", booking.interview_date)
    print("Interview Time:", booking.interview_time)

except Exception as error:
    print("Booking failed:", error)

finally:
    db.close()