from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.schemas.booking import BookingChatRequest
from app.database import get_db
from pydantic import BaseModel, Field, field_validator

from app.services.booking_conversation import (
    process_booking_message,
    process_booking_confirmation,
)


class BookingConfirmationRequest(BaseModel):
    conversation_id: str = Field(
        ...,
        min_length=1,
        description="Booking conversation ID.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Candidate's confirmation response.",
    )

    @field_validator("message", "conversation_id")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value

router = APIRouter(
    prefix="/booking",
    tags=["Interview Booking"],
)

@router.post("/chat")
async def booking_chat(
    request: BookingChatRequest,
    http_request: Request,
):
    """Collect interview booking details through conversation."""

    try:
        conversation_id = request.conversation_id or str(uuid4())

        redis_client = http_request.app.state.redis

        result = process_booking_message(
            redis_client=redis_client,
            conversation_id=conversation_id,
            message=request.message,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Booking conversation failed: {str(error)}",
        )

@router.post("/confirm")
async def confirm_booking(
    request: BookingConfirmationRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Confirm or cancel an interview booking."""

    try:
        redis_client = http_request.app.state.redis

        result = process_booking_confirmation(
            redis_client=redis_client,
            db=db,
            conversation_id=request.conversation_id,
            message=request.message,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Booking confirmation failed: {str(error)}",
        )