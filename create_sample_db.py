"""Build data/sample.db with a small, realistic-feeling dataset.

Runs at Railway build time (see railway.json). Each deploy gets a fresh
SQLite file, so the data resets on every redeploy — handy if the demo
needs a known starting state.

Schema:
    customers (id, name, region, signup_date)
    products  (id, name, category, price_cents)
    orders    (id, customer_id, product_id, quantity, order_date)

Money is INTEGER cents per the Knowledge-repo convention (CLAUDE.md).
"""
import os
import sqlite3

os.makedirs("data", exist_ok=True)
DB_PATH = "data/sample.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.executescript(
    """
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        id           INTEGER PRIMARY KEY,
        name         TEXT NOT NULL,
        region       TEXT NOT NULL,
        signup_date  TEXT NOT NULL
    );

    CREATE TABLE products (
        id           INTEGER PRIMARY KEY,
        name         TEXT NOT NULL,
        category     TEXT NOT NULL,
        price_cents  INTEGER NOT NULL
    );

    CREATE TABLE orders (
        id           INTEGER PRIMARY KEY,
        customer_id  INTEGER NOT NULL,
        product_id   INTEGER NOT NULL,
        quantity     INTEGER NOT NULL,
        order_date   TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id)  REFERENCES products(id)
    );
    """
)

cur.executemany(
    "INSERT INTO customers (name, region, signup_date) VALUES (?, ?, ?)",
    [
        ("Acme Corp", "North America", "2024-01-15"),
        ("Globex Industries", "Europe", "2024-02-20"),
        ("Initech", "North America", "2024-03-10"),
        ("Umbrella LLC", "Asia Pacific", "2024-04-05"),
        ("Stark Enterprises", "North America", "2024-05-18"),
        ("Wayne Industries", "North America", "2024-06-22"),
        ("Tyrell Corp", "Europe", "2024-07-30"),
        ("Cyberdyne Systems", "Asia Pacific", "2024-08-14"),
        ("Massive Dynamic", "Europe", "2024-09-09"),
        ("Soylent Corp", "North America", "2024-10-30"),
    ],
)

cur.executemany(
    "INSERT INTO products (name, category, price_cents) VALUES (?, ?, ?)",
    [
        ("Enterprise License",   "Software", 5_000_000),
        ("Consulting Package",   "Services", 2_500_000),
        ("Training Bundle",      "Services",   750_000),
        ("Support Plan",         "Services", 1_200_000),
        ("Cloud Migration",      "Services", 8_000_000),
        ("Data Pipeline Suite",  "Software", 3_500_000),
    ],
)

cur.executemany(
    "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
    [
        (1, 1, 2, "2025-01-15"),
        (1, 4, 1, "2025-02-01"),
        (2, 2, 3, "2025-01-20"),
        (3, 3, 5, "2025-03-10"),
        (4, 5, 1, "2025-04-22"),
        (5, 1, 1, "2025-05-05"),
        (5, 2, 2, "2025-05-12"),
        (6, 5, 1, "2025-06-18"),
        (7, 3, 4, "2025-07-02"),
        (8, 4, 2, "2025-07-15"),
        (1, 2, 1, "2025-08-01"),
        (2, 4, 2, "2025-08-20"),
        (3, 1, 1, "2025-09-05"),
        (9, 6, 3, "2025-10-12"),
        (10, 1, 4, "2025-11-03"),
        (10, 2, 1, "2025-11-28"),
        (9, 3, 8, "2026-01-15"),
        (6, 6, 2, "2026-02-08"),
        (4, 3, 6, "2026-02-22"),
        (7, 1, 1, "2026-03-14"),
    ],
)

con.commit()
con.close()
print(f"Sample DB created at {DB_PATH}")
