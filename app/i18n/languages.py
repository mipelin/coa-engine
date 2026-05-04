from __future__ import annotations

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "cs": "Czech",
    "ro": "Romanian",
    "hu": "Hungarian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "da": "Danish",
    "no": "Norwegian",
    "is": "Icelandic",
    "fi": "Finnish",
    "sv": "Swedish",
    "sq": "Albanian",
    "me": "Montenegrin",
    "mk": "Macedonian",
    "el": "Greek",
}


def resolve_language(language: str | None) -> tuple[str, str]:
    code = (language or "en").strip().lower()
    if code not in LANGUAGE_NAMES:
        return "en", LANGUAGE_NAMES["en"]
    return code, LANGUAGE_NAMES[code]


def final_language_instruction(language: str | None) -> str:
    _, language_name = resolve_language(language)
    return f"Respond ONLY in {language_name}. Do not switch languages."
