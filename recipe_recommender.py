"""
recipe_recommender.py
Recommends recipes based on ingredients that are expiring soon.
Uses TF-IDF vectorization + cosine similarity from scikit-learn.
"""

import sys
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Allow importing expiry_alert.py from the same 'modules' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import expiry_alert

# Path to the recipes dataset (relative to project root)
RECIPES_CSV_PATH = os.path.join("data", "recipes.csv")


def load_recipes():
    """Load the recipes dataset into a DataFrame."""
    if not os.path.exists(RECIPES_CSV_PATH):
        raise FileNotFoundError(
            f"Could not find {RECIPES_CSV_PATH}. "
            "Make sure recipes.csv is inside the data/ folder."
        )
    return pd.read_csv(RECIPES_CSV_PATH)


def build_query_text(expiring_items_df):
    """
    Combine the names of expiring/expired items into a single
    space-separated string, lowercased, to compare against recipes.
    """
    if expiring_items_df.empty:
        return ""

    item_names = expiring_items_df["item_name"].astype(str).str.lower().tolist()
    return " ".join(item_names)


def recommend_recipes(top_n=5, warning_days=3):
    """
    Main function: finds expiring items, then returns the top_n
    matching recipes ranked by ingredient similarity.
    """
    expiring_df = expiry_alert.get_expiring_items(warning_days)
    query_text = build_query_text(expiring_df)

    if query_text == "":
        return pd.DataFrame(columns=["recipe_name", "ingredients", "match_score"])

    recipes_df = load_recipes()

    # Combine query text with all recipe ingredient strings for vectorizing together
    documents = [query_text] + recipes_df["ingredients"].astype(str).str.lower().tolist()

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # First row (index 0) is our query; rest are recipes
    query_vector = tfidf_matrix[0]
    recipe_vectors = tfidf_matrix[1:]

    similarity_scores = cosine_similarity(query_vector, recipe_vectors)[0]

    results = recipes_df.copy()
    results["match_score"] = similarity_scores

    # Keep only recipes with some match, sorted highest first
    results = results[results["match_score"] > 0]
    results = results.sort_values(by="match_score", ascending=False)

    return results[["recipe_name", "ingredients", "match_score"]].head(top_n)


# ---- Quick test block ----
if __name__ == "__main__":
    print("Testing recipe_recommender module...\n")

    print("Expiring items being used for matching:")
    print(expiry_alert.get_expiring_items()[["item_name", "status", "days_left"]])

    print("\nRecommended Recipes:")
    recommendations = recommend_recipes(top_n=5)

    if recommendations.empty:
        print("No matching recipes found.")
    else:
        for _, row in recommendations.iterrows():
            print(f"- {row['recipe_name']} (match score: {row['match_score']:.2f})")
            print(f"  Ingredients: {row['ingredients']}")
