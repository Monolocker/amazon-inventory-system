import json
import csv
import os

inventory = {}

def load_inventory():
    # Guard clause: Check if file exists 
    if not os.path.exists("inventory.csv"):
        return 
    
    # Open CSV for reading 
    with open("inventory.csv", "r") as f:
        reader = csv.reader(f)

        # Skip header row
        next(reader)

        # Load each row into inventory
        for row in reader: 
            asin = row[0]
            location = row[1]
            quantity = int(row[2]) # Convert string to int

            inventory[asin] = {"location": location, "quantity": quantity} 

def save_inventory():
    # Open inventory.csv for writing (auto-closes when done)
    with open("inventory.csv", "w", newline = "") as f:
        # Create writer to handle CSV formatting
        writer = csv.writer(f)

        # Write header
        writer.writerow(["ASIN", "Location", "Quantity"])

        # Write each item
        for asin in inventory:
            location = inventory[asin]["location"]
            quantity = inventory[asin]["quantity"]
            writer.writerow([asin, location, quantity]) # Writes each item as a row

def add_item():
    # Get ASIN from user
    asin = input("Enter ASIN (or 'exit' to exit): ")
    if asin.lower() == "exit":
        print("Cancelled. Returning to menu.")
        return # Exit funciton, goes back to menu

    # Get the location from user
    location = input("Enter location (or 'exit' to exit): ")
    if location.lower() == "exit":
        print("Cancelled. Returning to menu.")
        return

    # Get input as string in case of potential exit before converting to int 
    quantity_input = input("Enter quantity (or 'exit' to exit) ")
    if quantity_input.lower() == "exit":
        print("Cancelled. Returning to menu.")
        return
    
    quantity = int(quantity_input) # Conversion after validation (no "exit")

    if asin in inventory:
        # Add to quantity if ASIN exists
        inventory[asin]["quantity"] += quantity
        inventory[asin]["location"] = location # Update location in case it moved 
        print(f"Added {quantity} more with ASIN: {asin}. Total now: {inventory[asin]['quantity']}x {asin} at {location}")
    else:
        # Initialize entry for new ASIN
        inventory[asin] = {"location": location, "quantity": quantity}
        print(f"Added {quantity}x {asin} to {location}")

    save_inventory()

def find_item():
    # Get ASIN with exit option
    asin = input("Enter ASIN (or 'exit' to exit): ")
    if asin.lower() == "exit":
        print("Cancelled. Returning to menu.")
        return

    if asin in inventory:
        location = inventory[asin]["location"] # Check before access, only runs if ASIN exists
        quantity = inventory[asin]["quantity"]
        print(f"Found {quantity}x {asin} at {location}")
    else: 
        print(f"{asin} was not found")

# Load existing inventory from CSV 
load_inventory()

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