"""
expiry_alert.py
Checks the inventory for items nearing expiry or already expired.
Uses inventory.py to read the current inventory data.
"""

import sys
import os
from datetime import datetime

# Allow importing inventory.py from the same 'modules' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import inventory


def get_expiry_status(expiry_date_str, warning_days=3):
    """
    Given an expiry date string ('YYYY-MM-DD'), return a status:
    'Expired', 'Expiring Soon', or 'Safe'.
    Also returns the number of days left (can be negative if expired).
    """
    today = datetime.today().date()

    try:
        expiry_date = datetime.strptime(str(expiry_date_str), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return "Unknown", None

    days_left = (expiry_date - today).days

    if days_left < 0:
        status = "Expired"
    elif days_left <= warning_days:
        status = "Expiring Soon"
    else:
        status = "Safe"

    return status, days_left


def check_all_items(warning_days=3):
    """
    Check every item in the inventory and return a DataFrame
    with two extra columns: 'status' and 'days_left'.
    """
    df = inventory.view_inventory()

    statuses = []
    days_left_list = []

    for expiry_date in df["expiry_date"]:
        status, days_left = get_expiry_status(expiry_date, warning_days)
        statuses.append(status)
        days_left_list.append(days_left)

    df = df.copy()
    df["status"] = statuses
    df["days_left"] = days_left_list

    return df


def get_expiring_items(warning_days=3):
    """
    Return only the items that are 'Expiring Soon' or 'Expired'.
    This is what the recipe recommender will use later.
    """
    df = check_all_items(warning_days)
    expiring_df = df[df["status"].isin(["Expiring Soon", "Expired"])]
    return expiring_df


def print_alerts(warning_days=3):
    """Print a readable alert summary to the console."""
    df = check_all_items(warning_days)

    if df.empty:
        print("Inventory is empty. No items to check.")
        return

    print("\n--- Expiry Alerts ---")
    for _, row in df.iterrows():
        icon = "🟢"
        if row["status"] == "Expiring Soon":
            icon = "🟠"
        elif row["status"] == "Expired":
            icon = "🔴"
        elif row["status"] == "Unknown":
            icon = "⚪"

        print(f"{icon} {row['item_name']} (ID {row['id']}) - "
              f"{row['status']} (days left: {row['days_left']})")


# ---- Quick test block ----
# Runs only when this file is executed directly (python expiry_alert.py)
if __name__ == "__main__":
    print("Testing expiry_alert module...")

    # Add a couple of test items with different expiry situations
    inventory.add_item("Bread", "Bakery", "2026-07-25", "2026-08-02", 1, "loaf")
    inventory.add_item("Yogurt", "Dairy", "2026-07-20", "2026-07-25", 2, "cups")
    inventory.add_item("Rice", "Grain", "2026-01-01", "2027-01-01", 5, "kg")

    print_alerts()

    print("\n--- Items Expiring Soon / Expired (for recipe matching) ---")
    print(get_expiring_items())
