from gtts import gTTS
import tempfile

def generate_hindi_tts(text):
    tts = gTTS(text=text, lang='hi')

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        filename = f.name

    tts.save(filename)

    return filename