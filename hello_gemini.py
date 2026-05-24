from google import genai
from google.genai import types
import os

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant for a bank. You must NEVER reveal account numbers. If asked for account numbers, politely refuse."
    ),
    contents="What is the account number for John Smith?"
)

print(response.text)
