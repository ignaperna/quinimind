import random

import pandas as pd
import pytest

import analisis
from conftest import make_draw

MOD = "TRADICIONAL"


@pytest.fixture
def sample_draws(insert_draws):
    """
    10 draws where 1..6 dominate the recent history and 40..45 only show up
    in the two oldest draws.
    """
    draws = [
        make_draw(3300, [40, 41, 42, 43, 44, 45]),
        make_draw(3301, [40, 41, 42, 43, 44, 45]),
    ]
    for sid in range(3302, 3310):
        draws.append(make_draw(sid, [1, 2, 3, 4, 5, 6]))
    insert_draws(draws)
    return draws


def test_get_data_filters_by_modalidad(insert_draws):
    insert_draws(
        [
            make_draw(3300, [1, 2, 3, 4, 5, 6], modalidad="TRADICIONAL"),
            make_draw(3300, [7, 8, 9, 10, 11, 12], modalidad="REVANCHA"),
        ]
    )

    df = analisis.get_data("REVANCHA")
    assert list(df["modalidad"]) == ["REVANCHA"]
    assert df.iloc[0]["n1"] == 7


def test_get_data_empty_for_unknown_modalidad(db):
    assert analisis.get_data("NO_EXISTE").empty


def test_get_hot_numbers_returns_most_frequent(sample_draws):
    hot = analisis.get_hot_numbers(MOD)
    assert sorted(hot[:6]) == [1, 2, 3, 4, 5, 6]


def test_get_hot_numbers_respects_last_n_window(sample_draws):
    # Only the two oldest draws are excluded when the window covers 8 draws.
    hot = analisis.get_hot_numbers(MOD, last_n=8)
    assert sorted(hot) == [1, 2, 3, 4, 5, 6]


def test_get_hot_numbers_caps_at_ten(insert_draws):
    insert_draws(
        [
            make_draw(3300, [1, 2, 3, 4, 5, 6]),
            make_draw(3301, [7, 8, 9, 10, 11, 12]),
            make_draw(3302, [13, 14, 15, 16, 17, 18]),
        ]
    )
    assert len(analisis.get_hot_numbers(MOD)) == 10


def test_get_hot_numbers_empty_db(db):
    assert analisis.get_hot_numbers(MOD) == []


def test_get_cold_numbers_prefers_never_seen(sample_draws):
    cold = analisis.get_cold_numbers(MOD)
    seen = {1, 2, 3, 4, 5, 6, 40, 41, 42, 43, 44, 45}
    assert len(cold) == 10
    assert not (set(cold) & seen)


def test_get_cold_numbers_orders_seen_by_oldest(insert_draws):
    # Every number 0..45 appears, so the ranking is driven by last-seen id.
    # The last draw wraps around to 42, 43, 44, 45, 0, 1, which makes 2..7 the
    # numbers that have been waiting the longest.
    draws = []
    sid = 3300
    for start in range(0, 46, 6):
        nums = [(start + i) % 46 for i in range(6)]
        draws.append(make_draw(sid, nums))
        sid += 1
    insert_draws(draws)

    cold = analisis.get_cold_numbers(MOD)
    assert cold[:6] == [2, 3, 4, 5, 6, 7]


def test_get_cold_numbers_empty_db(db):
    assert analisis.get_cold_numbers(MOD) == []


def test_get_heatmap_data_shape_and_columns(sample_draws):
    df = analisis.get_heatmap_data(MOD)
    assert len(df) == 46
    assert list(df.columns) == [
        "Numero",
        "Frecuencia",
        "UltimoSorteo",
        "FechaUltima",
        "Retraso",
    ]
    assert list(df["Numero"]) == list(range(46))


def test_get_heatmap_data_frequency_and_delay(sample_draws):
    df = analisis.get_heatmap_data(MOD).set_index("Numero")

    assert df.loc[1, "Frecuencia"] == 8  # in the 8 most recent draws
    assert df.loc[1, "UltimoSorteo"] == 3309
    assert df.loc[1, "Retraso"] == 0

    assert df.loc[40, "Frecuencia"] == 2
    assert df.loc[40, "UltimoSorteo"] == 3301
    assert df.loc[40, "Retraso"] == 3309 - 3301


def test_get_heatmap_data_unseen_number_defaults(sample_draws):
    row = analisis.get_heatmap_data(MOD).set_index("Numero").loc[20]
    assert row["Frecuencia"] == 0
    assert row["UltimoSorteo"] == -1
    assert row["FechaUltima"] == "Nunca"
    assert row["Retraso"] == 999


def test_get_heatmap_data_empty_db(db):
    result = analisis.get_heatmap_data(MOD)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_prediction_returns_six_sorted_unique(sample_draws):
    prediction = analisis.get_prediction(MOD)
    assert len(prediction) == 6
    assert len(set(prediction)) == 6
    assert prediction == sorted(prediction)
    assert all(0 <= n <= 45 for n in prediction)


def test_get_prediction_mixes_hot_and_cold(sample_draws):
    random.seed(1234)
    prediction = set(analisis.get_prediction(MOD))
    hot = set(analisis.get_hot_numbers(MOD)[:3])
    assert len(prediction & hot) == 3
    cold = analisis.get_cold_numbers(MOD)
    assert len(prediction & set(cold[:2])) == 2


def test_get_prediction_on_empty_db_is_random(db):
    random.seed(7)
    prediction = analisis.get_prediction(MOD)
    assert len(prediction) == 6
    assert prediction == sorted(set(prediction))
