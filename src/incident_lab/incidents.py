from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Callable

from .database import connect


@dataclass(frozen=True)
class Incident:
    key: str
    title: str
    symptom: str
    root_cause: str
    prevention: str
    investigation_sql: str


INCIDENTS = {
    "duplicate-payments": Incident("duplicate-payments", "Duplicate payments", "An order has two charges with the same external reference.", "No uniqueness constraint or idempotency check on the payment reference.", "Add a unique constraint and make payment ingestion idempotent.", "SELECT external_ref, COUNT(*) count FROM payments GROUP BY external_ref HAVING COUNT(*) > 1"),
    "inventory-discrepancy": Incident("inventory-discrepancy", "Inventory discrepancy", "Reserved stock exceeds stock on hand.", "Reservation update bypassed the availability check.", "Use an atomic conditional update and a CHECK/business invariant.", "SELECT * FROM inventory WHERE reserved > on_hand"),
    "slow-query": Incident("slow-query", "Slow customer lookup", "Email lookup performs a table scan.", "No index supports the email predicate.", "Create and monitor an index on customers(email).", "EXPLAIN QUERY PLAN SELECT * FROM customers WHERE email='naledi@example.test'"),
    "missing-index": Incident("missing-index", "Missing order index", "Customer order history scans orders.", "customer_id was not indexed.", "Add idx_orders_customer_id and review execution plans.", "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id=1"),
    "incorrect-total": Incident("incorrect-total", "Incorrect order total", "Stored total differs from line calculation.", "A manual price change did not recalculate the header.", "Calculate totals server-side in one transaction.", "SELECT o.id,o.total,SUM(i.quantity*i.unit_price) calculated FROM orders o JOIN order_items i ON i.order_id=o.id GROUP BY o.id HAVING o.total<>calculated"),
    "deadlock": Incident("deadlock", "Transaction deadlock", "Concurrent transfers lock resources in opposite order.", "Transactions acquire inventory rows in inconsistent order.", "Always lock rows by ascending product_id; retry deadlock victims.", "-- SQL Server: inspect sys.dm_tran_locks and the deadlock extended event"),
    "failed-import": Incident("failed-import", "Failed CSV import", "One malformed row aborts an import.", "Validation occurred during insertion rather than before it.", "Stage, validate, quarantine errors, then commit valid rows.", "SELECT * FROM audit_logs WHERE event_type='import_error'"),
    "duplicate-customer": Incident("duplicate-customer", "Duplicate customer", "The same email belongs to multiple customer records.", "Email normalization and uniqueness were missing.", "Normalize case/whitespace and enforce a unique email key.", "SELECT lower(trim(email)),COUNT(*) FROM customers GROUP BY lower(trim(email)) HAVING COUNT(*)>1"),
    "invalid-date": Incident("invalid-date", "Invalid order date", "An impossible date enters a text field.", "The SQLite demo accepts unvalidated date text.", "Validate ISO dates at the boundary; use DATE in SQL Server.", "SELECT * FROM orders WHERE date(order_date) IS NULL"),
    "failed-update": Incident("failed-update", "Failed order update", "An update changes status but not its audit record.", "Two statements ran outside one transaction.", "Wrap state and audit changes in a transaction with rollback.", "SELECT o.id FROM orders o LEFT JOIN audit_logs a ON a.entity_id=o.id AND a.event_type='order_updated' WHERE o.status='shipped' AND a.id IS NULL"),
}


def reproduce(path: str | Path, key: str) -> str:
    with closing(connect(path)) as db, db:
        if key == "duplicate-payments":
            db.execute("INSERT INTO payments(order_id,external_ref,amount,paid_at) VALUES(1,'PAY-001',207,'2026-10-01T10:01:00')")
        elif key == "inventory-discrepancy":
            db.execute("UPDATE inventory SET reserved=120 WHERE product_id=1")
        elif key in {"slow-query", "missing-index"}:
            return "Execution plan captured; no data changed."
        elif key == "incorrect-total":
            db.execute("UPDATE orders SET total=999 WHERE id=1")
        elif key == "deadlock":
            return "Simulation documented in sqlserver/deadlock_demo.sql; not forced in SQLite."
        elif key == "failed-import":
            import_customers(db, "name,email\nValid User,valid@example.test\nBroken,")
        elif key == "duplicate-customer":
            db.execute("INSERT INTO customers(name,email) VALUES('N. Mokoena',' NALEDI@example.test ')")
        elif key == "invalid-date":
            db.execute("INSERT INTO orders(customer_id,order_date,status,total) VALUES(1,'2026-99-42','open',0)")
        elif key == "failed-update":
            db.execute("UPDATE orders SET status='shipped' WHERE id=2")
        else:
            raise KeyError(key)
    return "Incident reproduced in the disposable demo database."


def import_customers(db: sqlite3.Connection, content: str) -> tuple[int, int]:
    valid = invalid = 0
    for row_number, row in enumerate(csv.DictReader(StringIO(content)), start=2):
        name, email = (row.get("name") or "").strip(), (row.get("email") or "").strip().lower()
        if not name or "@" not in email:
            invalid += 1
            db.execute("INSERT INTO audit_logs(event_type,details) VALUES('import_error',?)", (f"row {row_number}: invalid customer",))
            continue
        db.execute("INSERT INTO customers(name,email) VALUES(?,?)", (name, email))
        valid += 1
    return valid, invalid


def investigate(path: str | Path, key: str) -> list[dict[str, object]]:
    query = INCIDENTS[key].investigation_sql
    if query.startswith("--"):
        return []
    with closing(connect(path)) as db:
        cursor = db.execute(query)
        return [dict(row) for row in cursor.fetchall()]


def correct(path: str | Path, key: str) -> None:
    actions: dict[str, Callable[[sqlite3.Connection], None]] = {
        "duplicate-payments": lambda db: db.execute("DELETE FROM payments WHERE id NOT IN (SELECT MIN(id) FROM payments GROUP BY external_ref)"),
        "inventory-discrepancy": lambda db: db.execute("UPDATE inventory SET reserved=MIN(reserved,on_hand)"),
        "slow-query": lambda db: db.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)"),
        "missing-index": lambda db: db.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)"),
        "incorrect-total": lambda db: db.execute("UPDATE orders SET total=(SELECT SUM(quantity*unit_price) FROM order_items WHERE order_id=orders.id)"),
        "duplicate-customer": lambda db: db.execute("DELETE FROM customers WHERE id NOT IN (SELECT MIN(id) FROM customers GROUP BY lower(trim(email)))"),
        "invalid-date": lambda db: db.execute("DELETE FROM orders WHERE date(order_date) IS NULL"),
        "failed-update": lambda db: db.execute("INSERT INTO audit_logs(event_type,entity_id,details) SELECT 'order_updated',id,'backfilled audit event' FROM orders WHERE status='shipped'"),
    }
    if key in actions:
        with closing(connect(path)) as db, db:
            actions[key](db)

