from contextlib import closing

from incident_lab.database import connect, reset_database
from incident_lab.incidents import INCIDENTS, correct, import_customers, investigate, reproduce


def test_all_ten_incidents_are_documented():
    assert len(INCIDENTS) == 10


def test_duplicate_payment_reproduction_and_correction(tmp_path):
    db = tmp_path / "lab.db"
    reset_database(db)
    reproduce(db, "duplicate-payments")
    assert investigate(db, "duplicate-payments")[0]["count"] == 2
    correct(db, "duplicate-payments")
    assert investigate(db, "duplicate-payments") == []


def test_order_total_repair(tmp_path):
    db = tmp_path / "lab.db"
    reset_database(db)
    reproduce(db, "incorrect-total")
    assert investigate(db, "incorrect-total")
    correct(db, "incorrect-total")
    assert investigate(db, "incorrect-total") == []


def test_import_quarantines_invalid_rows(tmp_path):
    db_path = tmp_path / "lab.db"
    reset_database(db_path)
    with closing(connect(db_path)) as db, db:
        assert import_customers(db, "name,email\nGood,good@example.test\nBad,") == (1, 1)
        assert db.execute("SELECT COUNT(*) FROM audit_logs WHERE event_type='import_error'").fetchone()[0] == 1


def test_reset_is_disposable(tmp_path):
    db = tmp_path / "lab.db"
    reset_database(db)
    reproduce(db, "invalid-date")
    assert investigate(db, "invalid-date")
    reset_database(db)
    assert investigate(db, "invalid-date") == []

