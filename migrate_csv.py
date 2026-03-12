"""
One-time migration: inventory.csv -> SQLite.

Safety:
  1. Backs up inventory.csv to backups/ with timestamp.
  2. Reads CSV rows and inserts into SQLite.
  3. If duplicate asin+location rows exist, quantities are summed (safe merge).
  4. Original CSV is NOT deleted — you can remove it manually after verifying.

Run once:  python migrate_csv.py
"""
import csv
import os
import shutil
from datetime import datetime

from config import CSV_PATH, BACKUP_DIR, DATABASE_PATH
from db import init_db, get_connection


def backup_csv():
    """Copy inventory.csv to backups/ with a timestamp. Returns True if file existed."""
    if not os.path.exists(CSV_PATH):
        print("No inventory.csv found — nothing to migrate.")
        return False

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"inventory_backup_{timestamp}.csv")
    shutil.copy2(CSV_PATH, backup_path)
    print(f"✓ Backed up inventory.csv → {backup_path}")
    return True


def migrate():
    if not backup_csv():
        # No CSV means nothing to migrate; still init the DB for fresh start.
        init_db()
        print("Database initialized (empty).")
        return

    init_db()
    conn = get_connection()
    migrated = 0
    skipped = 0

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header

        for row in reader:
            if len(row) < 3:
                skipped += 1
                continue

            asin = row[0].strip()
            location = row[1].strip()

            try:
                quantity = int(row[2])
            except ValueError:
                print(f"  Skipping bad row: {row}")
                skipped += 1
                continue

            if quantity <= 0:
                print(f"  Skipping {asin} at {location}: qty {quantity} <= 0")
                skipped += 1
                continue

            # Safe merge: if asin+location already migrated, sum quantities
            existing = conn.execute(
                "SELECT id, quantity FROM inventory WHERE asin = ? AND location = ?",
                (asin, location),
            ).fetchone()

            if existing:
                new_qty = existing["quantity"] + quantity
                conn.execute(
                    "UPDATE inventory SET quantity = ? WHERE id = ?",
                    (new_qty, existing["id"]),
                )
                print(f"  Merged duplicate: {asin} at {location} → qty {new_qty}")
            else:
                conn.execute(
                    "INSERT INTO inventory (asin, location, quantity) VALUES (?, ?, ?)",
                    (asin, location, quantity),
                )

            migrated += 1

    conn.commit()
    conn.close()
    print(f"\n✓ Migration complete: {migrated} rows migrated, {skipped} skipped.")
    print(f"  Database: {DATABASE_PATH}")
    print(f"  Original CSV preserved (not deleted).")


if __name__ == "__main__":
    migrate()