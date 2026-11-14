import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )


# Configure Gemini client
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=120000
    ),
)

MODEL_NAME = "gemini-3.5-flash-lite"


try:
    print("Sending request to Gemini...")
    print("Model:", MODEL_NAME)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Reply with exactly: Hello from Gemini.",
        config=types.GenerateContentConfig(
            max_output_tokens=100,
            temperature=0.2,
        ),
    )

    print("\nGEMINI RESPONSE")

    # Check generated text
    if response.text:
        print("Generated Text:")
        print(response.text)

    else:
        print("No text returned.")

        # Inspect response candidates
        if response.candidates:
            for candidate in response.candidates:
                print("\nFinish Reason:", candidate.finish_reason)
                print("Content:", candidate.content)
        else:
            print("No response candidates returned.")

    # Inspect prompt feedback
    print("\nPROMPT FEEDBACK")
    print(response.prompt_feedback)

    print("\nTEST COMPLETED")

except Exception as error:
    print("\nGEMINI REQUEST FAILED")
    print("Error Type:", type(error).__name__)
    print("Error Details:", str(error))

finally:
    client.close()
    print("\nGemini client closed.")