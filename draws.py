"""Helpers shared by the analysis, API and scraping modules."""

import pandas as pd

from constants import MODE_KEYS, NUMBER_COLUMNS


def numbers_of_row(row):
    """Returns the six drawn numbers of a DataFrame row (or plain dict)."""
    return [row[col] for col in NUMBER_COLUMNS]


def numbers_of_sorteo(sorteo):
    """Returns the six drawn numbers of a Sorteo record."""
    return [sorteo.n1, sorteo.n2, sorteo.n3, sorteo.n4, sorteo.n5, sorteo.n6]


def melt_numbers(df):
    """Flattens the number columns of a DataFrame into a single Series."""
    return pd.melt(df, value_vars=NUMBER_COLUMNS)['value']


def last_seen(df):
    """
    Returns (last_seen_id, last_seen_date): for every number, the id and date of
    the most recent draw it appeared in.
    """
    df_sorted = df.sort_values(by='sorteo_id', ascending=True)

    last_id = {}
    last_date = {}
    for _, row in df_sorted.iterrows():
        for n in numbers_of_row(row):
            last_id[n] = row['sorteo_id']
            last_date[n] = row['fecha']

    return last_id, last_date


def mode_key(modalidad):
    """Maps a modality name (any casing/wording) to its camelCase feed key."""
    upper = modalidad.upper()
    if "SEGUNDA" in upper:
        return MODE_KEYS["LA SEGUNDA"]
    if "REVANCHA" in upper:
        return MODE_KEYS["REVANCHA"]
    if "SIEMPRE" in upper:
        return MODE_KEYS["SIEMPRE SALE"]
    return MODE_KEYS["TRADICIONAL"]
