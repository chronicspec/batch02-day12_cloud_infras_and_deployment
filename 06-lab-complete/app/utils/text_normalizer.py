import re
import unicodedata


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    return re.sub(r"\s+", " ", normalized)


def normalize_for_matching(value: str) -> str:
    normalized = normalize_text(value)
    stripped = "".join(
        char for char in unicodedata.normalize("NFD", normalized) if unicodedata.category(char) != "Mn"
    )
    return stripped.replace("đ", "d")
