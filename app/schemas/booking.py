from datetime import date, time
import re

from pydantic import BaseModel, Field, field_validator


class BookingRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the interview candidate."
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Email address of the interview candidate."
    )

    interview_date: date = Field(
        ...,
        description="Preferred interview date in YYYY-MM-DD format."
    )

    interview_time: time = Field(
        ...,
        description="Preferred interview time in HH:MM format."
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()

        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        if not re.fullmatch(email_pattern, value):
            raise ValueError("Please provide a valid email address.")

        return value

    @field_validator("interview_date")
    @classmethod
    def validate_interview_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Interview date cannot be in the past.")

        return value

class BookingDetailsExtraction(BaseModel):
    """Schema for extracting partial booking details from conversation."""

    name: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    interview_date: date | None = None
    interview_time: time | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if len(value) < 2:
            raise ValueError("Name must contain at least 2 characters.")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()

        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        if not re.fullmatch(email_pattern, value):
            raise ValueError("Please provide a valid email address.")

        return value

    @field_validator("interview_date")
    @classmethod
    def validate_interview_date(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise ValueError("Interview date cannot be in the past.")

        return value

class BookingChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="Candidate's booking conversation message.",
    )

    conversation_id: str | None = Field(
        default=None,
        description="Existing conversation ID for continuing a booking.",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value