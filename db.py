"""
Database layer for inventory system.

- SAFE FOR PRODUCTION LATER: all DB access is in one module.
- When deploying, swap SQLite for PostgreSQL here only.
- Uses parameterized queries (no SQL injection risk).
"""
import sqlite3
from config import DATABASE_PATH


def get_connection():
    """Return a connection with row_factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the inventory table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            asin     TEXT    NOT NULL,
            location TEXT    NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            UNIQUE(asin, location)
        )
    """)
    conn.commit()
    conn.close()


def add_item(asin, location, quantity):
    """
    Add quantity at a specific location.
    If the asin+location combo exists, ADD to existing quantity.
    Never overwrites other locations for the same ASIN.
    """
    if quantity <= 0:
        return {"success": False, "error": "Quantity must be positive."}

    conn = get_connection()
    row = conn.execute(
        "SELECT id, quantity FROM inventory WHERE asin = ? AND location = ?",
        (asin, location),
    ).fetchone()

    if row:
        new_qty = row["quantity"] + quantity
        conn.execute(
            "UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row["id"])
        )
    else:
        conn.execute(
            "INSERT INTO inventory (asin, location, quantity) VALUES (?, ?, ?)",
            (asin, location, quantity),
        )

    conn.commit()
    conn.close()
    return {"success": True}


def find_item(asin):
    """Return list of {location, quantity} dicts for an ASIN."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT location, quantity FROM inventory WHERE asin = ? ORDER BY location",
        (asin,),
    ).fetchall()
    conn.close()
    return [{"location": r["location"], "quantity": r["quantity"]} for r in rows]


def get_total_quantity(asin):
    """Return total quantity across all locations for an ASIN."""
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory WHERE asin = ?",
        (asin,),
    ).fetchone()
    conn.close()
    return row["total"]


def remove_item(asin, location, quantity):
    """
    Remove quantity from a specific location.
    - Deletes the location row when its quantity hits 0.
    - Reports whether the ASIN was fully deleted (no stock anywhere).
    """
    if quantity <= 0:
        return {"success": False, "error": "quantity_invalid"}

    conn = get_connection()
    row = conn.execute(
        "SELECT id, quantity FROM inventory WHERE asin = ? AND location = ?",
        (asin, location),
    ).fetchone()

    if not row:
        conn.close()
        return {"success": False, "error": "not_found"}

    current_qty = row["quantity"]

    if quantity > current_qty:
        conn.close()
        return {"success": False, "error": "exceeds", "available": current_qty}

    new_qty = current_qty - quantity

    if new_qty == 0:
        conn.execute("DELETE FROM inventory WHERE id = ?", (row["id"],))
    else:
        conn.execute(
            "UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row["id"])
        )

    conn.commit()

    # Check if ASIN still exists anywhere
    remaining = conn.execute(
        "SELECT COUNT(*) AS cnt FROM inventory WHERE asin = ?", (asin,)
    ).fetchone()["cnt"]

    conn.close()

    return {
        "success": True,
        "removed": quantity,
        "remaining_at_location": new_qty,
        "asin_deleted": remaining == 0,
    }


def view_all():
    """Return all inventory rows sorted by ASIN then location."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT asin, location, quantity FROM inventory ORDER BY asin, location"
    ).fetchall()
    conn.close()
    return [
        {"asin": r["asin"], "location": r["location"], "quantity": r["quantity"]}
        for r in rows
    ]