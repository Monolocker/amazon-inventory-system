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
    asin = input("Enter or scan ASIN (or 'exit' to exit): ")
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

def remove_item():
    asin = input("Enter ASIN (or 'exit' to exit): ")
    if asin.lower() == "exit":
        print("Cancelled. Returning to menu.")
        return
    
    # Check if ASIN exists
    if asin not in inventory:
        print(f"{asin} not found in inventory.")
        return 
    
    # Show current quantity for context
    current_qty = inventory[asin]["quantity"]
    location = inventory[asin]["location"]
    print(f"Currently have {current_qty}x {asin} at {location}")

    while True:
        qty_input = input("How many to remove (or 'exit' to exit): ")

        if qty_input.lower() == "exit":
            print("Cancelled. Returning to menu.")
            return
        
        if qty_input.isdigit():
            quantity = int(qty_input)
            if quantity > 0:
                break
            else: 
                print("Error: Enter a positive non-zero number")
        else: 
            print("Error. Invalid quantity. Please enter a number")
    
    new_qty = current_qty - quantity # what is in inventory - what is being removed

    if quantity == current_qty: 
        # Exact match: remove all without warning
        del inventory[asin]
        print(f"Removed {current_qty}x {asin}. ASIN deleted from inventory.")
    elif quantity > current_qty:
        # Trying to remove more than available, ask confirmation
        confirm = input(f"Only {current_qty} available. Remove all? (yes/no): ")
        if confirm.lower() == "yes":
            # Confirmed. Remove all
            del inventory[asin]
            print(f"Removed all {current_qty}x {asin}. ASIN deleted from inventory.")
        else: 
            # confirm == no
            print("Cancelled. Returning to menu.")
            return 
    else: 
        # Normal reduction quantity < current_qty
        inventory[asin]["quantity"] = new_qty
        print(f"Removed {quantity}x {asin}. {new_qty}x {asin} remaining at {location}")

    # Save changes to CSV
    save_inventory()

def view_all_items():
    # Check if empty
    if len(inventory) == 0:
        print("Inventory is empty.")
        return
    
    # Print header 
    print("\n=== Current Inventory ===")
    print(f"\n{'ASIN':<12} | {'Location':<10} | {'Quantity':<8}")
    print("-" * 40)

    # Print each item (similar to save_inventory)
    for asin in inventory:
        location = inventory[asin]["location"]
        quantity = inventory[asin]["quantity"]
        print(f"{asin:<12} | {location:<10} | {quantity:<8}")

    print() # Blank line at end

# Load existing inventory from CSV 
load_inventory()


running = True

while running:
    print("=== Amazon Inventory System ===")
    print("1. Add Item")
    print("2. Find Item")
    print("3. Remove Item")
    print("4. View All Items")
    print("5. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_item()
    elif choice == "2":
        find_item()
    elif choice == "3":
        remove_item()
    elif choice == "4":
        view_all_items()
    elif choice == "5":
        running = False
        print("Exiting... Goodbye!")
    else:
        print("Invalid option. Please try again.")