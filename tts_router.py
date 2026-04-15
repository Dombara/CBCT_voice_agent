from tts_azure import generate_hindi_tts
from tts_deepgram import generate_english_tts
from language_detector import detect_language
from utils.audio_utils import convert_to_mulaw


def generate_speech(text):
    lang = detect_language(text)

    print(f"[TTS ROUTER] Detected language: {lang}")

    if lang == "hi":
        wav_file = generate_hindi_tts(text)
    else:
        wav_file = generate_english_tts(text)

    raw_file = convert_to_mulaw(wav_file)

    return raw_file