from uuid import uuid4
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import InterviewBooking


def save_booking(
    db: Session,
    booking_state: dict,
) -> InterviewBooking:
    """Save a confirmed interview booking to MySQL."""

    if booking_state.get("status") != "confirmed":
        raise ValueError(
            "Only confirmed bookings can be saved."
        )

    booking = InterviewBooking(
        booking_id=str(uuid4()),
        name=booking_state["name"],
        email=booking_state["email"],
        interview_date=date.fromisoformat(
            booking_state["interview_date"]
        ),
        interview_time=time.fromisoformat(
            booking_state["interview_time"]
        ),
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    except SQLAlchemyError:
        db.rollback()
        raise