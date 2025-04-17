from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_language(text):
    """Detect the language of the given text using GPT."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a language detection assistant."},
                {"role": "user", "content": f"Detect the language of the following text: {text}"}
            ]
        )
        detected_language = response.choices[0].message.content.strip()
        return detected_language
    except Exception as e:
        return "unknown"