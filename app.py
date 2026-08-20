"""
app.py
Main Flask application for the AI Food Waste Reduction Assistant.
Connects inventory.py, expiry_alert.py, and recipe_recommender.py
to render web pages.
"""

import sys
import os
from flask import Flask, render_template, request, redirect, url_for

# Allow importing our modules from the 'modules' folder
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

import inventory
import expiry_alert
import recipe_recommender

app = Flask(__name__)


@app.route("/")
def home():
    """Home / dashboard page."""
    df = inventory.view_inventory()
    total_items = len(df)

    status_df = expiry_alert.check_all_items()
    expiring_count = len(status_df[status_df["status"].isin(["Expiring Soon", "Expired"])])

    # Category breakdown (for bar chart)
    if not df.empty:
        category_counts = df["category"].value_counts()
        category_labels = category_counts.index.tolist()
        category_values = category_counts.values.tolist()
    else:
        category_labels = []
        category_values = []

    # Status breakdown (for pie chart)
    if not status_df.empty:
        status_counts = status_df["status"].value_counts()
        status_labels = status_counts.index.tolist()
        status_values = status_counts.values.tolist()
    else:
        status_labels = []
        status_values = []

    # Recently added items (last 5, based on highest IDs)
    recent_items = df.sort_values(by="id", ascending=False).head(5).to_dict(orient="records")

    return render_template(
        "index.html",
        total_items=total_items,
        expiring_count=expiring_count,
        category_labels=category_labels,
        category_values=category_values,
        status_labels=status_labels,
        status_values=status_values,
        recent_items=recent_items
    )


@app.route("/inventory", methods=["GET", "POST"])
def inventory_page():
    """View and add inventory items."""
    if request.method == "POST":
        item_name = request.form.get("item_name")
        category = request.form.get("category")
        purchase_date = request.form.get("purchase_date")
        expiry_date = request.form.get("expiry_date")
        quantity = request.form.get("quantity")
        unit = request.form.get("unit")

        inventory.add_item(item_name, category, purchase_date, expiry_date, quantity, unit)
        return redirect(url_for("inventory_page"))

    items = inventory.view_inventory().to_dict(orient="records")
    return render_template("inventory.html", items=items)


@app.route("/delete/<int:item_id>")
def delete_item_route(item_id):
    """Delete an inventory item by ID."""
    inventory.delete_item(item_id)
    return redirect(url_for("inventory_page"))


@app.route("/alerts")
def alerts_page():
    """Show expiry alerts for all items."""
    df = expiry_alert.check_all_items()
    items = df.to_dict(orient="records")
    return render_template("alerts.html", items=items)


@app.route("/recipes")
def recipes_page():
    """Show recommended recipes based on expiring items."""
    recommendations = recipe_recommender.recommend_recipes(top_n=5)
    recipes = recommendations.to_dict(orient="records")
    return render_template("recipes.html", recipes=recipes)


if __name__ == "__main__":
    app.run(debug=True)
