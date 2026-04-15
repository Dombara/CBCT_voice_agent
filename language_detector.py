def detect_language(text):
    text = text.lower()

    # Strong Hindi signals (Hinglish included)
    hindi_markers = [
        "hai", "haan", "nahi", "kya", "kaise", "mujhe",
        "aap", "kal", "baje", "chahiye", "karna", "naam"
    ]

    score = 0

    for word in hindi_markers:
        if word in text:
            score += 1

    # 🔥 threshold-based detection
    if score >= 2:
        return "hi"

    return "en"