import json

inventory = {}

def add_item():
    # Get ASIN from user
    asin = input("Enter ASIN: ")

    # Get the location from user
    location = input("Enter location: ")

    # Get quantity from user 
    quantity = int(input("Enter quantity: "))

    if asin in inventory:
        # add to quantity if ASIN exists
        inventory[asin]["quantity"] += quantity
        inventory[asin]["location"] = location # Update location in case it moved 
        print(f"Added {quantity} more with ASIN: {asin}. Total now: {inventory[asin]['quantity']}x {asin} at {location}")
    else:
        # initialize entry for new ASIN
        inventory[asin] = {"location": location, "quantity": quantity}
        print(f"Added {quantity}x {asin} to {location}")

def find_item():
    print("Find item feature coming soon...")

running = True

while running:
    print("=== Amazon Inventory System ===")
    print("1. Add Item")
    print("2. Find Item")
    print("3. Exit")
    print("4. [DEBUG] Show all inventory")

    choice = input("Choose an option: ")

    if choice == "1":
        add_item()
    elif choice == "2":
        find_item()
    elif choice == "3":
        running = False  # This exits the loop
        print("Exiting... Goodbye!")
    elif choice == "4":
        print(json.dumps(inventory, indent=2))
    else:
        print("Invalid option. Please try again.")