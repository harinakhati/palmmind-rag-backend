import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

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