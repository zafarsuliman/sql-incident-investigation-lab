from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL);
CREATE TABLE products(id INTEGER PRIMARY KEY, sku TEXT NOT NULL UNIQUE, name TEXT NOT NULL, price NUMERIC NOT NULL CHECK(price >= 0));
CREATE TABLE inventory(product_id INTEGER PRIMARY KEY REFERENCES products(id), on_hand INTEGER NOT NULL CHECK(on_hand >= 0), reserved INTEGER NOT NULL DEFAULT 0 CHECK(reserved >= 0));
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id), order_date TEXT NOT NULL, status TEXT NOT NULL, total NUMERIC NOT NULL);
CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id), quantity INTEGER NOT NULL CHECK(quantity > 0), unit_price NUMERIC NOT NULL);
CREATE TABLE payments(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), external_ref TEXT NOT NULL, amount NUMERIC NOT NULL, paid_at TEXT NOT NULL);
CREATE TABLE suppliers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, score NUMERIC NOT NULL);
CREATE TABLE audit_logs(id INTEGER PRIMARY KEY, event_type TEXT NOT NULL, entity_id INTEGER, details TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""

SEED = """
INSERT INTO customers VALUES (1,'Naledi Mokoena','naledi@example.test'),(2,'Aiden Naidoo','aiden@example.test'),(3,'Thandi Jacobs','thandi@example.test');
INSERT INTO products VALUES (1,'SKU-100','Safety Gloves',75.00),(2,'SKU-200','Packing Tape',28.50),(3,'SKU-300','Hand Truck',1450.00);
INSERT INTO inventory VALUES (1,100,10),(2,200,20),(3,8,1);
INSERT INTO orders VALUES (1,1,'2026-10-01','paid',207.00),(2,2,'2026-10-02','open',1450.00);
INSERT INTO order_items VALUES (1,1,1,2,75.00),(2,1,2,2,28.50),(3,2,3,1,1450.00);
INSERT INTO payments VALUES (1,1,'PAY-001',207.00,'2026-10-01T10:00:00');
INSERT INTO suppliers VALUES (1,'Ubuntu Industrial Supply',0.94),(2,'Cape Trade Goods',0.88);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def reset_database(path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    with closing(connect(target)) as connection:
        with connection:
            connection.executescript(SCHEMA)
            connection.executescript(SEED)

