"""
Configuration for Amazon Inventory System.

- LOCAL-ONLY for now: paths default to project directory.
- SAFE FOR PRODUCTION LATER: uses env vars so nothing is hardcoded.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database path (override with INVENTORY_DB env var for testing/production)
DATABASE_PATH = os.environ.get("INVENTORY_DB", os.path.join(BASE_DIR, "inventory.db"))

# Legacy CSV path (used only during migration)
CSV_PATH = os.path.join(BASE_DIR, "inventory.csv")

# Backup directory for migration
BACKUP_DIR = os.path.join(BASE_DIR, "backups")