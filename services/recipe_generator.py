import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()


class RecipeGenerator:
    def __init__(self, pantry_df):
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("Spoonacular API key not found in environment variables")

        self.pantry_items = self._clean_pantry_items(pantry_df)
        print("🥫 Pantry items used for search:", self.pantry_items)

    def _clean_pantry_items(self, pantry_df):
        """Clean and prepare pantry items for API search"""
        items = []
        for item in pantry_df["Item Name"].dropna():
            if isinstance(item, str) and item.strip():
                # Basic cleaning - keep most characters, just lowercase
                cleaned = re.sub(r'[^\w\s-]', '', item.lower()).strip()
                if cleaned:  # Only add if not empty after cleaning
                    items.append(cleaned)
        return list(set(items))  # Remove duplicates

    def find_recipes(self, number=5, diet=None, intolerances=None, meal_type=None):
        """Find recipes using Spoonacular API

        Args:
            number (int): Max number of recipes to return.
            diet (str, optional): Diet restriction (e.g., "vegetarian").
            intolerances (list, optional): List of allergies/intolerances.
            meal_type (str, optional): Meal type filter (e.g., "salad", "main course").

        Returns:
            list: Complete recipes details as dictionaries.
        """
        if not self.pantry_items or len(self.pantry_items) < 1:
            print("⚠️ Not enough pantry items.")
            return []

        # Use the findByIngredients endpoint which is more flexible
        url = "https://api.spoonacular.com/recipes/findByIngredients"

        params = {
            "apiKey": self.api_key,
            "ingredients": ",".join(self.pantry_items[:20]),  # Limit to first 20 items
            "number": min(number * 2, 10),  # Request extra results to allow filtering later
            "ignorePantry": True,  # Ignore common pantry staples
            "ranking": 2,  # Maximize used ingredients
            "limitLicense": False
        }

        if diet:
            params["diet"] = diet
        if intolerances:
            params["intolerances"] = ",".join(intolerances)
        if meal_type:
            # Spoonacular expects meal type filtering as the "type" parameter
            params["type"] = meal_type

        print("📡 Querying Spoonacular with parameters:")
        for k, v in params.items():
            if k != "apiKey":  # Do not print the API key
                print(f"  {k}: {v}")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raises exception for bad status codes

            recipes = response.json()
            print(f"🔍 Received {len(recipes) if isinstance(recipes, list) else 0} raw recipes")

            if not recipes:
                return []

            # Get full details for each recipe (since findByIngredients returns limited info)
            detailed_recipes = []
            for recipe in recipes[:number]:  # Only get details for the number we need
                try:
                    detail = self._get_recipe_details(recipe['id'])
                    if detail:
                        detailed_recipes.append(detail)
                except Exception as e:
                    print(f"⚠️ Couldn't get details for recipe {recipe['id']}: {str(e)}")
                    continue

            print(f"✅ Found {len(detailed_recipes)} complete recipes")
            return detailed_recipes

        except requests.exceptions.RequestException as e:
            print(f"🚨 API Request failed: {str(e)}")
            return []

    def _get_recipe_details(self, recipe_id):
        """Get full details for a specific recipe"""
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {
            "apiKey": self.api_key,
            "includeNutrition": False
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            recipe = response.json()

            # Ensure we have required fields
            if not all(key in recipe for key in ['title', 'extendedIngredients', 'instructions']):
                return None

            return {
                "id": recipe.get("id"),
                "title": recipe.get("title"),
                "image": recipe.get("image"),
                "extendedIngredients": recipe.get("extendedIngredients", []),
                "instructions": recipe.get("instructions", ""),
                "sourceUrl": recipe.get("sourceUrl", "")
            }
        except Exception as e:
            print(f"⚠️ Couldn't get details for recipe {recipe_id}: {str(e)}")
            return None