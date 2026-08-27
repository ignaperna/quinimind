from conftest import make_draw


def test_sorteo_repr():
    from database import Sorteo

    sorteo = Sorteo(sorteo_id=3300, modalidad="TRADICIONAL")
    assert repr(sorteo) == "<Sorteo(id=3300, mod=TRADICIONAL)>"


def test_init_db_creates_table(db):
    from sqlalchemy import inspect

    db.Base.metadata.drop_all(bind=db.engine)
    db.init_db()
    assert "sorteos" in inspect(db.engine).get_table_names()


def test_guardar_sorteo_persists_all_fields(db):
    db.guardar_sorteo(make_draw(3301, [1, 2, 3, 4, 5, 6], fecha="01/02/2025"))

    session = db.SessionLocal()
    try:
        stored = session.query(db.Sorteo).one()
    finally:
        session.close()

    assert (stored.sorteo_id, stored.modalidad, stored.fecha) == (
        3301,
        "TRADICIONAL",
        "01/02/2025",
    )
    assert [stored.n1, stored.n2, stored.n3, stored.n4, stored.n5, stored.n6] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_guardar_sorteo_skips_duplicate_same_modality(db, capsys):
    db.guardar_sorteo(make_draw(3302, [1, 2, 3, 4, 5, 6]))
    db.guardar_sorteo(make_draw(3302, [7, 8, 9, 10, 11, 12]))
    out = capsys.readouterr().out

    session = db.SessionLocal()
    try:
        rows = session.query(db.Sorteo).all()
        assert len(rows) == 1
        assert rows[0].n1 == 1  # original row untouched
    finally:
        session.close()
    assert "Skipped duplicate" in out


def test_guardar_sorteo_allows_same_draw_other_modality(db):
    db.guardar_sorteo(make_draw(3303, [1, 2, 3, 4, 5, 6], modalidad="TRADICIONAL"))
    db.guardar_sorteo(make_draw(3303, [7, 8, 9, 10, 11, 12], modalidad="REVANCHA"))

    session = db.SessionLocal()
    try:
        assert session.query(db.Sorteo).count() == 2
    finally:
        session.close()


def test_guardar_sorteo_swallows_errors(db, capsys):
    db.guardar_sorteo({"sorteo_id": 3304})  # missing keys
    out = capsys.readouterr().out

    session = db.SessionLocal()
    try:
        assert session.query(db.Sorteo).count() == 0
    finally:
        session.close()
    assert "Error saving" in out
