import unicodedata

SEGMENTED_BUTTON_STYLE = """
QPushButton {
    padding: 6px 12px;
    border: 1px solid #888;
    background: #eee;
    color: #222;
}
QPushButton:checked {
    background: #4a90d9;
    color: white;
    border: 1px solid #2f6fb3;
}
"""


def strip_accents(text):
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))
