from uuid import uuid4

from app.database import SessionLocal
from app.services.redis_service import (
    get_redis_client,
    get_booking_state,
    clear_booking_state,
)

from app.services.booking_conversation import (
    process_booking_message,
    process_booking_confirmation,
)


redis_client = get_redis_client()
db = SessionLocal()
conversation_id = str(uuid4())

try:
    # Step 1: Collect all booking details.
    result = process_booking_message(
        redis_client,
        conversation_id,
        (
            "My name is Test Candidate. "
            "My email is testcandidate@example.com. "
            "I prefer November 20, 2026, at 2:30 PM."
        ),
    )

    print("\nBooking Details:")
    print(result)

    # Step 2: Send an unclear confirmation response.
    result = process_booking_confirmation(
        redis_client,
        db,
        conversation_id,
        "Maybe later",
    )

    print("\nUnclear Confirmation:")
    print(result)

    # Verify booking state still exists.
    print("\nRedis State After Unclear Response:")
    print(get_booking_state(redis_client, conversation_id))

    # Step 3: Explicitly confirm the booking.
    result = process_booking_confirmation(
        redis_client,
        db,
        conversation_id,
        "Yes",
    )

    print("\nFinal Confirmation:")
    print(result)

    # Step 4: Verify Redis state was cleared.
    print("\nRedis State After Confirmation:")
    print(get_booking_state(redis_client, conversation_id))

finally:
    clear_booking_state(redis_client, conversation_id)
    db.close()