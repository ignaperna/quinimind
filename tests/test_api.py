import pytest
from fastapi.testclient import TestClient

import api
from conftest import make_draw


@pytest.fixture
def client(db):
    return TestClient(api.app)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "system": "QuiniMind AI"}


def test_update_success(client, monkeypatch):
    calls = []
    monkeypatch.setattr(api.scrape_quini6, "run_scraper", lambda: calls.append(1))

    response = client.get("/update")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert calls == [1]


def test_update_propagates_scraper_failure(client, monkeypatch):
    def boom():
        raise RuntimeError("scraper down")

    monkeypatch.setattr(api.scrape_quini6, "run_scraper", boom)

    response = client.get("/update")
    assert response.status_code == 500
    assert response.json()["detail"] == "scraper down"


def test_latest_without_data(client):
    assert client.get("/latest").json() == {"error": "No data found"}


def test_latest_returns_all_modalities_of_newest_draw(client, insert_draws):
    insert_draws(
        [
            make_draw(3300, [1, 2, 3, 4, 5, 6], fecha="01/01/2025"),
            make_draw(3301, [7, 8, 9, 10, 11, 12], "TRADICIONAL", "08/01/2025"),
            make_draw(3301, [13, 14, 15, 16, 17, 18], "LA SEGUNDA", "08/01/2025"),
            make_draw(3301, [19, 20, 21, 22, 23, 24], "REVANCHA", "08/01/2025"),
            make_draw(3301, [25, 26, 27, 28, 29, 30], "SIEMPRE SALE", "08/01/2025"),
        ]
    )

    body = client.get("/latest").json()
    assert body["id"] == 3301
    assert body["date"] == "08/01/2025"
    assert body["modes"] == {
        "tradicional": [7, 8, 9, 10, 11, 12],
        "laSegunda": [13, 14, 15, 16, 17, 18],
        "revancha": [19, 20, 21, 22, 23, 24],
        "siempreSale": [25, 26, 27, 28, 29, 30],
    }


def test_latest_maps_unknown_modality_to_tradicional(client, insert_draws):
    insert_draws([make_draw(3302, [1, 2, 3, 4, 5, 6], modalidad="OTRA COSA")])

    assert list(client.get("/latest").json()["modes"]) == ["tradicional"]


def test_history_empty(client):
    assert client.get("/history").json() == []


def test_history_is_ordered_newest_first_with_tradicional_numbers(
    client, insert_draws
):
    insert_draws(
        [
            make_draw(3300, [1, 2, 3, 4, 5, 6], "TRADICIONAL", "01/01/2025"),
            make_draw(3300, [40, 41, 42, 43, 44, 45], "REVANCHA", "01/01/2025"),
            make_draw(3301, [7, 8, 9, 10, 11, 12], "TRADICIONAL", "08/01/2025"),
        ]
    )

    history = client.get("/history").json()
    assert [entry["id"] for entry in history] == [3301, 3300]
    assert history[0] == {
        "id": 3301,
        "date": "08/01/2025",
        "numbers": [7, 8, 9, 10, 11, 12],
    }
    assert history[1]["numbers"] == [1, 2, 3, 4, 5, 6]


def test_history_falls_back_to_other_modality(client, insert_draws):
    insert_draws([make_draw(3303, [1, 2, 3, 4, 5, 6], modalidad="REVANCHA")])

    assert client.get("/history").json()[0]["numbers"] == [1, 2, 3, 4, 5, 6]


def test_history_respects_limit(client, insert_draws):
    insert_draws(
        [make_draw(sid, [1, 2, 3, 4, 5, 6]) for sid in range(3300, 3305)]
    )

    history = client.get("/history", params={"limit": 2}).json()
    assert [entry["id"] for entry in history] == [3304, 3303]


def test_heatmap_empty(client):
    assert client.get("/stats/heatmap").json() == []


def test_heatmap_returns_record_per_number(client, insert_draws):
    insert_draws([make_draw(3300, [1, 2, 3, 4, 5, 6])])

    records = client.get("/stats/heatmap").json()
    assert len(records) == 46
    assert records[1]["Numero"] == 1
    assert records[1]["Frecuencia"] == 1
    assert records[0]["Retraso"] == 999


def test_heatmap_normalizes_modalidad_case(client, insert_draws):
    insert_draws([make_draw(3300, [1, 2, 3, 4, 5, 6], modalidad="REVANCHA")])

    assert client.get("/stats/heatmap", params={"modalidad": "revancha"}).json()
    assert client.get("/stats/heatmap", params={"modalidad": "tradicional"}).json() == []


def test_predict_returns_six_unique_numbers(client, insert_draws):
    insert_draws(
        [make_draw(sid, [1, 2, 3, 4, 5, 6]) for sid in range(3300, 3305)]
    )

    prediction = client.get("/predict").json()
    assert len(prediction) == 6
    assert len(set(prediction)) == 6
    assert prediction == sorted(prediction)
    assert all(0 <= n <= 45 for n in prediction)
