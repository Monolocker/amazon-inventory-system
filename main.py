def add_item():
    print("Add item feature coming soon...")

def find_item():
    print("Find item feature coming soon...")

running = True

while running:
    print("=== Amazon Inventory System ===")
    print("1. Add Item")
    print("2. Find Item")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_item()
    elif choice == "2":
        find_item()
    elif choice == "3":
        running = False  # This exits the loop
        print("Exiting... Goodbye!")
    else:
        print("Invalid option. Please try again.")