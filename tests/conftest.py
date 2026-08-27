import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# database.py creates the engine and the tables at import time, so the test
# database has to be configured before any module imports it.
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_DB_FD)
os.environ["QUINIMIND_DATABASE_URL"] = f"sqlite:///{_DB_PATH}"

import database  # noqa: E402


def pytest_sessionfinish(session, exitstatus):
    database.engine.dispose()
    if os.path.exists(_DB_PATH):
        os.remove(_DB_PATH)


@pytest.fixture
def db():
    """Empty database, recreated for every test."""
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield database
    database.Base.metadata.drop_all(bind=database.engine)


def make_draw(sorteo_id, numbers, modalidad="TRADICIONAL", fecha=None):
    n1, n2, n3, n4, n5, n6 = numbers
    return {
        "fecha": fecha or f"{sorteo_id:02d}/01/2025",
        "sorteo_id": sorteo_id,
        "modalidad": modalidad,
        "n1": n1,
        "n2": n2,
        "n3": n3,
        "n4": n4,
        "n5": n5,
        "n6": n6,
    }


@pytest.fixture
def insert_draws(db):
    def _insert(draws):
        for draw in draws:
            db.guardar_sorteo(draw)

    return _insert
