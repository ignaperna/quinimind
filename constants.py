"""Shared constants for the QuiniMind data pipeline, API and UIs."""

# Columns holding the drawn numbers of a single draw.
NUMBER_COLUMNS = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']

# Numbers per draw and valid number range (Quini 6 uses 00-45).
NUMBERS_PER_DRAW = len(NUMBER_COLUMNS)
MAX_NUMBER = 45
ALL_NUMBERS = list(range(MAX_NUMBER + 1))

# Display names of the four modalities, in draw order.
MODALIDADES = ["TRADICIONAL", "LA SEGUNDA", "REVANCHA", "SIEMPRE SALE"]

# Display name -> camelCase key used by the JSON feed and the frontends.
MODE_KEYS = {
    "TRADICIONAL": "tradicional",
    "LA SEGUNDA": "laSegunda",
    "REVANCHA": "revancha",
    "SIEMPRE SALE": "siempreSale",
}

DEFAULT_MODALIDAD = "TRADICIONAL"
