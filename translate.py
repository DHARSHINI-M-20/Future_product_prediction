import re
from deep_translator import GoogleTranslator
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator

# --- Helpers ---
TA_RANGE = re.compile(r"[\u0B80-\u0BFF]")  # Tamil Unicode block

def is_tamil(text: str) -> bool:
    return bool(TA_RANGE.search(text))

def tokenize_keep_punct(s: str):
    # words (letters+digits+apostrophes) OR single non-space char (punct)
    return re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9]", s)

# --- Translators ---
def translate_tamil_to_english(text: str) -> str:
    """Tamil (Unicode) → English using Google Translate."""
    return GoogleTranslator(source="ta", target="en").translate(text)

def tanglish_to_tamil(text: str) -> str:
    """Tanglish (romanized Tamil) → Tamil (Unicode) using ITRANS mapping."""
    tokens = tokenize_keep_punct(text)
    out = []
    for tok in tokens:
        # transliterate only alphabetic chunks; keep punctuation as-is
        if re.fullmatch(r"[A-Za-z']+", tok):
            try:
                out.append(UnicodeIndicTransliterator.transliterate(tok, "itrans", "tam"))
            except Exception:
                out.append(tok)  # fallback if transliteration fails
        else:
            out.append(tok)
    return "".join(out)

# --- Public APIs you’ll call ---
def translate_tamil_text(text: str) -> str:
    """Tamil script → English"""
    return translate_tamil_to_english(text)

def translate_tanglish_text(text: str) -> str:
    """Tanglish → Tamil → English"""
    ta = tanglish_to_tamil(text)
    return translate_tamil_to_english(ta)

def translate_mixed_text(text: str) -> str:
    """
    Mixed English + Tanglish + Tamil → English.
    Strategy: convert all roman chunks to Tamil, keep Tamil as-is, then translate.
    """
    tokens = tokenize_keep_punct(text)
    tamilified = []
    for tok in tokens:
        if is_tamil(tok):
            tamilified.append(tok)
        elif re.fullmatch(r"[A-Za-z']+", tok):
            # treat as Tanglish word; transliterate to Tamil
            try:
                tamilified.append(UnicodeIndicTransliterator.transliterate(tok, "itrans", "tam"))
            except Exception:
                tamilified.append(tok)  # leave as-is if it looks like real English
        else:
            tamilified.append(tok)
    tamil_line = "".join(tamilified)
    return translate_tamil_to_english(tamil_line)

# --- Demo ---
if __name__ == "__main__":
    tamil = "நீங்கள் எப்படி இருக்கிறீர்கள்?"
    tanglish = "neenga epdi irukeenga?"
    mixed = "sir repeat panna sonnaru"

    print("Tamil → English :", translate_tamil_text(tamil))
    print("Tanglish → English :", translate_tanglish_text(tanglish))
    print("Mixed → English :", translate_mixed_text(mixed))
