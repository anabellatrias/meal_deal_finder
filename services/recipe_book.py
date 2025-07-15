class RecipeBook:
    def __init__(self, session_state):
        self.session_state = session_state
        if 'recipe_book' not in self.session_state:
            self.session_state.recipe_book = []

    def save_recipe(self, recipe_details):
        # Check if recipe already exists
        if any(r.get("id") == recipe_details.get("id") for r in self.session_state.recipe_book):
            return False

        recipe_data = {
            "id": recipe_details.get("id", f"custom_{len(self.session_state.recipe_book)}"),
            "title": recipe_details["title"],
            "image": recipe_details.get("image", ""),
            "ingredients": [i.get("original", i.get("name", "Unknown"))
                            for i in recipe_details.get("extendedIngredients", [])],
            "ingredient_names": [i.get("name", "").lower()
                                 for i in recipe_details.get("extendedIngredients", [])],
            "instructions": recipe_details.get("instructions", "No instructions provided."),
            "meal_type": recipe_details.get("mealType", "unspecified"),
            "source": "api"
        }

        self.session_state.recipe_book.append(recipe_data)
        return True

    def get_saved_recipes(self):
        return self.session_state.recipe_book

    def remove_recipe(self, recipe_id):
        self.session_state.recipe_book = [
            r for r in self.session_state.recipe_book if r["id"] != recipe_id
        ]

    def plan_meal(self, recipe_id, pantry_manager):
        recipe = next((r for r in self.session_state.recipe_book if r["id"] == recipe_id), None)
        if not recipe:
            return False

        pantry_items = [i.lower() for i in pantry_manager.get_pantry()["Item Name"].str.lower()]
        missing_ingredients = []

        for ing in recipe.get("ingredient_names", []):
            if not any(pantry_item in ing for pantry_item in pantry_items):
                missing_ingredients.append(ing)

        return missing_ingredients