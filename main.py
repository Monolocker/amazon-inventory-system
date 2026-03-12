"""
CLI interface for Amazon Inventory System.

- Uses SQLite via db.py (replaces old CSV approach).
- LOCAL-ONLY: this CLI will be replaced by Flask routes in Milestone 2.
- Run: python main.py
"""
from db import init_db, add_item, find_item, remove_item, view_all, get_total_quantity


def cli_add():
    asin = input("Enter or scan ASIN (or 'exit'): ").strip()
    if asin.lower() == "exit":
        return

    location = input("Enter location (or 'exit'): ").strip().upper()
    if location.upper() == "EXIT":
        return

    qty_input = input("Enter quantity (or 'exit'): ").strip()
    if qty_input.lower() == "exit":
        return

    try:
        quantity = int(qty_input)
        if quantity <= 0:
            print("Error: quantity must be a positive number.")
            return
    except ValueError:
        print("Error: invalid number.")
        return

    add_item(asin, location, quantity)
    total = get_total_quantity(asin)
    print(f"✓ Added {quantity}x {asin} at {location}. Total across all locations: {total}")


def cli_find():
    asin = input("Enter ASIN (or 'exit'): ").strip()
    if asin.lower() == "exit":
        return

    locations = find_item(asin)
    if not locations:
        print(f"{asin} not found.")
        return

    total = sum(loc["quantity"] for loc in locations)
    print(f"\n{asin} — Total: {total}")
    for loc in locations:
        print(f"  {loc['location']}: {loc['quantity']}")


def cli_remove():
    asin = input("Enter ASIN (or 'exit'): ").strip()
    if asin.lower() == "exit":
        return

    locations = find_item(asin)
    if not locations:
        print(f"{asin} not found.")
        return

    # Show current state
    total = sum(loc["quantity"] for loc in locations)
    print(f"\n{asin} — Total: {total}")
    for loc in locations:
        print(f"  {loc['location']}: {loc['quantity']}")

    location = input("Remove from which location? (or 'exit'): ").strip().upper()
    if location.upper() == "EXIT":
        return

    qty_input = input("Quantity to remove (or 'exit'): ").strip()
    if qty_input.lower() == "exit":
        return

    try:
        quantity = int(qty_input)
        if quantity <= 0:
            print("Error: quantity must be a positive number.")
            return
    except ValueError:
        print("Error: invalid number.")
        return

    result = remove_item(asin, location, quantity)

    if not result["success"]:
        if result["error"] == "not_found":
            print(f"{asin} not found at {location}.")
        elif result["error"] == "exceeds":
            print(f"Only {result['available']} available at {location}.")
        return

    if result["asin_deleted"]:
        print(f"✓ Removed {result['removed']}x {asin} from {location}. ASIN fully deleted.")
    elif result["remaining_at_location"] == 0:
        print(f"✓ Removed {result['removed']}x {asin} from {location}. Location removed.")
    else:
        print(
            f"✓ Removed {result['removed']}x {asin} from {location}. "
            f"{result['remaining_at_location']} remaining at {location}."
        )


def cli_view_all():
    items = view_all()
    if not items:
        print("Inventory is empty.")
        return

    print(f"\n{'ASIN':<15} | {'Location':<10} | {'Qty':<6}")
    print("-" * 36)
    for item in items:
        print(f"{item['asin']:<15} | {item['location']:<10} | {item['quantity']:<6}")
    print()


def main():
    init_db()

    while True:
        print("\n=== Amazon Inventory System ===")
        print("1. Add Item")
        print("2. Find Item")
        print("3. Remove Item")
        print("4. View All")
        print("5. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            cli_add()
        elif choice == "2":
            cli_find()
        elif choice == "3":
            cli_remove()
        elif choice == "4":
            cli_view_all()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()