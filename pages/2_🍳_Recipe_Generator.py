import streamlit as st
from services.pantry_manager import PantryManager
from services.recipe_generator import RecipeGenerator
from services.shopping_cart import ShoppingCart
from services.recipe_book import RecipeBook

st.set_page_config(page_title="Recipe Generator", layout="centered")

# Initialize services
pantry_manager = PantryManager(st.session_state)
cart = ShoppingCart(st.session_state)
recipe_book = RecipeBook(st.session_state)

st.title("🍳 Recipe Generator")
st.markdown("Recipes based on your pantry, diet, and allergies.")

# --- Load Pantry ---
pantry_df = pantry_manager.get_pantry()

if pantry_df.empty:
    st.warning("Your pantry is empty. Add ingredients in the Pantry Manager.")
    st.stop()

# --- Filters Form ---
with st.form("filter_form"):
    st.subheader("⚙️ Recipe Filters")

    col1, col2 = st.columns(2)

    diet = col1.selectbox("Dietary Preference", [
        "", "vegetarian", "vegan", "pescetarian", "ketogenic", "gluten free"
    ])

    intolerances = col2.multiselect("Allergies / Intolerances", [
        "dairy", "egg", "gluten", "grain", "peanut", "seafood", "sesame",
        "shellfish", "soy", "sulfite", "tree nut", "wheat"
    ])

    meal_type = st.selectbox("Meal Type", [
        "", "main course", "side dish", "dessert", "appetizer",
        "salad", "bread", "breakfast", "soup", "beverage", "sauce", "marinade"
    ])

    submitted = st.form_submit_button("🔄 Generate Recipes")

if submitted:
    generator = RecipeGenerator(pantry_df)
    recipes = generator.find_recipes(
        number=5,
        diet=diet if diet else None,
        intolerances=intolerances,
        meal_type=meal_type if meal_type else None
    )

    if not recipes:
        st.error("🚫 No recipes found. Try fewer restrictions or different pantry items.")
    else:
        st.session_state.generated_recipes = recipes  # Store for button actions

if 'generated_recipes' in st.session_state:
    recipes = st.session_state.generated_recipes
    st.success(f"✅ Found {len(recipes)} recipes.")

    for recipe in recipes:
        with st.expander(recipe["title"]):
            st.image(recipe["image"], width=300)

            st.subheader("📝 Ingredients")
            pantry_items = [i.lower() for i in pantry_df["Item Name"].str.lower()]
            missing_ingredients = []

            for ing in recipe.get("extendedIngredients", []):
                ing_name = ing.get('original', ing.get('name', 'Unknown')).lower()
                if not any(pantry_item in ing_name for pantry_item in pantry_items):
                    missing_ingredients.append(ing.get('original', ing.get('name', 'Unknown')))
                st.markdown(f"- {ing.get('original', ing.get('name', 'Unknown'))}")

            st.subheader("📋 Instructions")
            st.markdown(recipe.get("instructions", "No instructions provided."), unsafe_allow_html=True)

            # Action buttons
            col1, col2 = st.columns(2)

            # Add missing ingredients button
            if missing_ingredients:
                if col1.button("🛒 Add Missing Ingredients", key=f"add_{recipe['id']}"):
                    cart.add_missing_ingredients(missing_ingredients)
                    st.success(f"Added {len(missing_ingredients)} ingredients to cart!")

            # Save recipe button
            if col2.button("📚 Save Recipe", key=f"save_{recipe['id']}"):
                recipe_book.save_recipe(recipe)
                st.success("Recipe saved to your recipe book!")

            # Prevent form resubmission on button click