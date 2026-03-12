"""
Tests for the inventory database layer.

Run:  python -m pytest tests/test_db.py -v
  or: python -m unittest tests.test_db -v
"""
import os
import sys
import unittest

# Use a throwaway test database (never touches real data)
os.environ["INVENTORY_DB"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test_inventory.db"
)

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db import init_db, add_item, find_item, remove_item, view_all, get_total_quantity


class TestInventoryDB(unittest.TestCase):
    """Each test gets a fresh empty database."""

    def setUp(self):
        db_path = os.environ["INVENTORY_DB"]
        if os.path.exists(db_path):
            os.remove(db_path)
        init_db()

    def tearDown(self):
        db_path = os.environ["INVENTORY_DB"]
        if os.path.exists(db_path):
            os.remove(db_path)

    # ── Add ──────────────────────────────────────────────

    def test_add_new_item(self):
        add_item("B0X", "A1", 5)
        locs = find_item("B0X")
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0]["location"], "A1")
        self.assertEqual(locs[0]["quantity"], 5)

    def test_add_same_location_sums_quantity(self):
        add_item("B0X", "A1", 3)
        add_item("B0X", "A1", 2)
        locs = find_item("B0X")
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0]["quantity"], 5)

    def test_add_multiple_locations_never_overwrites(self):
        """CRITICAL BUSINESS RULE: B0X at A1(1) + B0X at C3(2) => both kept, total 3."""
        add_item("B0X", "A1", 1)
        add_item("B0X", "C3", 2)
        locs = find_item("B0X")
        self.assertEqual(len(locs), 2)
        self.assertEqual(get_total_quantity("B0X"), 3)

    def test_add_zero_quantity_rejected(self):
        result = add_item("B0X", "A1", 0)
        self.assertFalse(result["success"])

    def test_add_negative_quantity_rejected(self):
        result = add_item("B0X", "A1", -1)
        self.assertFalse(result["success"])

    # ── Find ─────────────────────────────────────────────

    def test_find_existing(self):
        add_item("B0X", "A1", 3)
        locs = find_item("B0X")
        self.assertEqual(len(locs), 1)

    def test_find_nonexistent(self):
        self.assertEqual(find_item("NOPE"), [])

    def test_total_quantity_across_locations(self):
        add_item("B0X", "A1", 2)
        add_item("B0X", "C3", 4)
        self.assertEqual(get_total_quantity("B0X"), 6)

    def test_total_quantity_nonexistent(self):
        self.assertEqual(get_total_quantity("NOPE"), 0)

    # ── Remove ───────────────────────────────────────────

    def test_remove_partial(self):
        add_item("B0X", "A1", 5)
        result = remove_item("B0X", "A1", 2)
        self.assertTrue(result["success"])
        self.assertEqual(result["remaining_at_location"], 3)
        self.assertFalse(result["asin_deleted"])

    def test_remove_all_from_one_location_keeps_other(self):
        add_item("B0X", "A1", 3)
        add_item("B0X", "C3", 2)
        result = remove_item("B0X", "A1", 3)
        self.assertTrue(result["success"])
        self.assertEqual(result["remaining_at_location"], 0)
        self.assertFalse(result["asin_deleted"])
        # C3 should still be there
        locs = find_item("B0X")
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0]["location"], "C3")

    def test_remove_last_quantity_deletes_asin(self):
        add_item("B0X", "A1", 3)
        result = remove_item("B0X", "A1", 3)
        self.assertTrue(result["success"])
        self.assertTrue(result["asin_deleted"])
        self.assertEqual(find_item("B0X"), [])

    def test_remove_exceeds_quantity(self):
        add_item("B0X", "A1", 2)
        result = remove_item("B0X", "A1", 5)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "exceeds")
        self.assertEqual(result["available"], 2)

    def test_remove_nonexistent_asin(self):
        result = remove_item("NOPE", "A1", 1)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "not_found")

    def test_remove_wrong_location(self):
        add_item("B0X", "A1", 5)
        result = remove_item("B0X", "Z9", 1)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "not_found")

    # ── View All ─────────────────────────────────────────

    def test_view_all_empty(self):
        self.assertEqual(view_all(), [])

    def test_view_all_sorted(self):
        add_item("B0Y", "B2", 3)
        add_item("B0X", "A1", 1)
        add_item("B0X", "C3", 2)
        items = view_all()
        self.assertEqual(len(items), 3)
        # Should be sorted by asin then location
        self.assertEqual(items[0]["asin"], "B0X")
        self.assertEqual(items[0]["location"], "A1")
        self.assertEqual(items[1]["asin"], "B0X")
        self.assertEqual(items[1]["location"], "C3")
        self.assertEqual(items[2]["asin"], "B0Y")


if __name__ == "__main__":
    unittest.main()