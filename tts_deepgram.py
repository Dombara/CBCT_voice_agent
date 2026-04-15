import requests
import tempfile
import os

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def generate_english_tts(text):
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json={"text": text})

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(response.content)
        return f.name