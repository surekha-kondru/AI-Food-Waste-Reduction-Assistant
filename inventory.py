"""
inventory.py
Handles all inventory operations (add, view, update, delete)
for the AI Food Waste Reduction Assistant.
Data is stored in data/inventory.csv using Pandas.
"""

import pandas as pd
import os
from datetime import datetime

# Path to the CSV file (relative to project root)
CSV_PATH = os.path.join("data", "inventory.csv")


def load_inventory():
    """Load the inventory CSV into a DataFrame."""
    if not os.path.exists(CSV_PATH):
        # If file doesn't exist yet, create an empty one with headers
        df = pd.DataFrame(columns=[
            "id", "item_name", "category",
            "purchase_date", "expiry_date", "quantity", "unit"
        ])
        df.to_csv(CSV_PATH, index=False)
        return df

    return pd.read_csv(CSV_PATH)


def save_inventory(df):
    """Save the DataFrame back to the CSV file."""
    df.to_csv(CSV_PATH, index=False)


def get_next_id(df):
    """Generate the next available ID."""
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


def add_item(item_name, category, purchase_date, expiry_date, quantity, unit):
    """
    Add a new food item to the inventory.
    Dates should be in 'YYYY-MM-DD' format.
    """
    df = load_inventory()
    new_id = get_next_id(df)

    new_row = {
        "id": new_id,
        "item_name": item_name,
        "category": category,
        "purchase_date": purchase_date,
        "expiry_date": expiry_date,
        "quantity": quantity,
        "unit": unit
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_inventory(df)
    print(f"Added item: {item_name} (ID: {new_id})")
    return new_id


def view_inventory():
    """Return the full inventory as a DataFrame."""
    df = load_inventory()
    return df


def update_item(item_id, **kwargs):
    """
    Update fields of an existing item by its ID.
    Example: update_item(1, quantity=5, unit="kg")
    """
    df = load_inventory()

    if item_id not in df["id"].values:
        print(f"No item found with ID {item_id}")
        return False

    for key, value in kwargs.items():
        if key in df.columns:
            df.loc[df["id"] == item_id, key] = value

    save_inventory(df)
    print(f"Updated item ID {item_id}")
    return True


def delete_item(item_id):
    """Delete an item from the inventory by its ID."""
    df = load_inventory()

    if item_id not in df["id"].values:
        print(f"No item found with ID {item_id}")
        return False

    df = df[df["id"] != item_id]
    save_inventory(df)
    print(f"Deleted item ID {item_id}")
    return True


# ---- Quick test block ----
# This only runs if you execute this file directly (python inventory.py)
# It won't run when imported into app.py later.
if __name__ == "__main__":
    print("Testing inventory module...\n")

    # Add a couple of sample items
    add_item("Tomatoes", "Vegetable", "2026-07-28", "2026-08-05", 6, "pcs")
    add_item("Milk", "Dairy", "2026-07-30", "2026-08-03", 1, "l")

    print("\nCurrent Inventory:")
    print(view_inventory())

    print("\nUpdating item ID 1 quantity to 10...")
    update_item(1, quantity=10)

    print("\nCurrent Inventory after update:")
    print(view_inventory())

    print("\nDeleting item ID 2...")
    delete_item(2)

    print("\nFinal Inventory:")
    print(view_inventory())
