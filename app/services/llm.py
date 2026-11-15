import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from datetime import date
from pydantic import ValidationError

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")

MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=120000
    ),
)

def generate_answer(
    query: str,
    retrieved_chunks: list[dict],
    conversation_history: list[dict] | None = None,
) -> str:

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    # Handle missing conversation history
    if conversation_history is None:
        conversation_history = []

    # Handle cases where no relevant document chunks are found
    if not retrieved_chunks:
        return "I couldn't find relevant information in the uploaded documents to answer your question."

    # Prepare document context
    context = "\n\n".join(
        [
            f"Document: {chunk.get('filename', 'Unknown')}\n"
            f"Content: {chunk['chunk_text']}"
            for chunk in retrieved_chunks
        ]
    )

    # Prepare previous conversation
    history = "\n".join(
        [
            f"{message['role'].capitalize()}: {message['content']}"
            for message in conversation_history
        ]
    )

    if not history:
        history = "No previous conversation."

    # Construct prompt
    prompt = f"""
You are PalmMind, an intelligent document-based assistant.

Your task is to answer the user's question using the provided document context
and relevant previous conversation.

IMPORTANT RULES:
1. Use the provided document context as the primary source of information.
2. You may use previous conversation to understand references and follow-up questions.
3. Do not invent facts that are not supported by the documents.
4. If the documents do not contain the answer, clearly say so.
5. Keep your answer clear, relevant, and easy to understand.

PREVIOUS CONVERSATION:
{history}

DOCUMENT CONTEXT:
{context}

CURRENT USER QUESTION:
{query}

ANSWER:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0.2,
            "max_output_tokens": 300,
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text

import json

from app.schemas.booking import BookingDetailsExtraction

def extract_booking_details(message: str) -> dict:
    """Extract and independently validate interview booking details."""

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    today = date.today().isoformat()

    prompt = f"""
You are an information extraction assistant.

Extract interview booking details from the user's message.

The possible fields are:
- name
- email
- interview_date
- interview_time

Rules:
1. Extract only information explicitly provided by the user.
2. Do not invent missing information.
3. Use null for fields that are not provided.
4. Return interview_date in YYYY-MM-DD format.
5. Return interview_time in 24-hour HH:MM format.
6. Today's date is {today}.
7. Interpret relative dates using today's date.
8. If a date or time is ambiguous, return null for that field.
9. Return valid JSON only.

User message:
{message}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty extraction response.")

    extracted_data = json.loads(response.text)

    validated_data = {}
    validation_errors = {}

    fields = (
        "name",
        "email",
        "interview_date",
        "interview_time",
    )

    for field in fields:
        value = extracted_data.get(field)

        if value is None:
            validated_data[field] = None
            continue

        try:
            field_result = BookingDetailsExtraction.model_validate(
                {field: value}
            )

            validated_data[field] = field_result.model_dump(
                mode="json"
            )[field]

        except ValidationError as error:
            validated_data[field] = None

            validation_errors[field] = error.errors()[0]["msg"]

    return {
        **validated_data,
        "_validation_errors": validation_errors,
    }