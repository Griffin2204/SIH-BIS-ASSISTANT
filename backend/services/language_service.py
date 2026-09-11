import re
from typing import Dict, Any, Optional, List

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"code": "en", "name": "English", "native_name": "English"},
    "hi": {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
    "mr": {"code": "mr", "name": "Marathi", "native_name": "मराठी"},
}

DEFAULT_LANGUAGE = "en"

# Unicode regex patterns
LATIN_REGEX = re.compile(r'[a-zA-Z]')
DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')

# Marathi specific character: 'ळ' (U+0933)
MARATHI_SPECIFIC_CHARS = {'ळ'}

# Common Marathi grammatical words, pronouns, postpositions, and verb forms
MARATHI_MARKERS = {
    'आहे', 'आहेत', 'नाही', 'काय', 'कसे', 'कशी', 'कसा', 'करावे', 'बद्दल',
    'माहिती', 'म्हणजे', 'मध्ये', 'करा', 'होते', 'केले', 'सांगा', 'मिळेल',
    'लागतात', 'द्या', 'यांची', 'त्यांची', 'कोणते', 'कोणती', 'कशासाठी',
    'येथे', 'कधी', 'कसं', 'आहोत', 'नाहीत', 'झाले', 'झाली', 'करू',
    'शकतो', 'शकते', 'करणे', 'असेल', 'नसून', 'वारंवार', 'कशात'
}

# Common Hindi grammatical words, pronouns, postpositions, and verb forms
HINDI_MARKERS = {
    'है', 'हैं', 'नहीं', 'क्या', 'कैसे', 'कैसी', 'कैसा', 'करना', 'बारे',
    'जानकारी', 'मतलब', 'में', 'करें', 'था', 'थी', 'थे', 'किए', 'बताएं',
    'बताइए', 'मिलेगा', 'लगते', 'लगता', 'दें', 'दीजिए', 'इनकी', 'उनकी',
    'कौनसा', 'कौनसी', 'सकते', 'सकता', 'सकती', 'होगा', 'होगी', 'होंगे',
    'हुआ', 'हुई', 'कहाँ', 'कब', 'चाहिए', 'होता', 'होती', 'जिसमें'
}


class LanguageService:
    _instance: Optional['LanguageService'] = None

    @classmethod
    def get_instance(cls) -> 'LanguageService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Returns the dictionary of supported language definitions."""
        return SUPPORTED_LANGUAGES

    def is_supported(self, lang_code: str) -> bool:
        """Checks if a language code is supported."""
        if not lang_code:
            return False
        return lang_code.strip().lower() in SUPPORTED_LANGUAGES

    def validate_language(self, lang_code: Optional[str]) -> Optional[str]:
        """
        Validates language code.
        Returns cleaned code if valid.
        Raises ValueError if provided code is unsupported.
        Returns None if input is None or empty.
        """
        if lang_code is None:
            return None
        clean = lang_code.strip().lower()
        if not clean:
            return None
        if clean not in SUPPORTED_LANGUAGES:
            supported_list = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
            raise ValueError(f"Unsupported language code '{lang_code}'. Supported languages are: {supported_list}")
        return clean

    def detect_language(self, text: str) -> str:
        """
        Lightweight deterministic language detector:
        - Detects English (Latin script)
        - Detects Hindi vs Marathi in Devanagari script using linguistic heuristics
        - Returns 'en', 'hi', 'mr', or 'unknown'
        """
        if not text or not text.strip():
            return "unknown"

        cleaned_text = text.strip()

        latin_count = len(LATIN_REGEX.findall(cleaned_text))
        devanagari_count = len(DEVANAGARI_REGEX.findall(cleaned_text))

        # If no letters found at all
        if latin_count == 0 and devanagari_count == 0:
            return "unknown"

        # If predominantly Latin script
        if latin_count > devanagari_count:
            return "en"

        # If Devanagari script is present
        # Check for Marathi specific character 'ळ'
        for ch in cleaned_text:
            if ch in MARATHI_SPECIFIC_CHARS:
                return "mr"

        # Tokenize text into words for lexical heuristic comparison
        # Remove punctuation and split on whitespace
        words = re.findall(r'[\u0900-\u097F]+', cleaned_text)
        if not words:
            return "unknown"

        marathi_score = 0
        hindi_score = 0

        for w in words:
            if w in MARATHI_MARKERS:
                marathi_score += 2
            if w in HINDI_MARKERS:
                hindi_score += 2

        if marathi_score > hindi_score:
            return "mr"
        elif hindi_score > marathi_score:
            return "hi"
        else:
            # Fallback: if Devanagari but no decisive markers, default to 'hi'
            # as it is the broader national standard language for Devanagari queries
            return "hi"

    def resolve_language(self, text: str, explicit_lang: Optional[str] = None) -> str:
        """
        Resolves language priority:
        1. Explicit override if provided and valid.
        2. Automatic detection from text.
        3. Fallback to default language ('en').
        """
        if explicit_lang is not None and explicit_lang.strip():
            valid = self.validate_language(explicit_lang)
            if valid:
                return valid

        detected = self.detect_language(text)
        if detected in SUPPORTED_LANGUAGES:
            return detected

        return DEFAULT_LANGUAGE

    def get_language_name(self, lang_code: str) -> str:
        """Returns the full display name for a language code (e.g. 'Hindi')."""
        clean = (lang_code or "").strip().lower()
        if clean in SUPPORTED_LANGUAGES:
            return SUPPORTED_LANGUAGES[clean]["name"]
        return "English"


language_service = LanguageService.get_instance()
