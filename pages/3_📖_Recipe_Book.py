import streamlit as st
from services.recipe_book import RecipeBook
from services.pantry_manager import PantryManager

st.set_page_config(page_title="Recipe Book", layout="centered")

recipe_book = RecipeBook(st.session_state)
pantry = PantryManager(st.session_state)
recipes = recipe_book.get_saved_recipes()

st.title("📖 Your Recipe Book")

# --- Add Custom Recipe ---
with st.expander("📥 Add Your Own Recipe"):
    with st.form("custom_recipe_form"):
        title = st.text_input("🍽 Recipe Name")

        st.markdown("### 🧾 Ingredients")
        ingredient_names = []
        ingredient_quantities = []
        ingredient_units = []

        cols = st.columns([3, 2, 2])
        with cols[0]:
            ingredient_names = st.text_area("Ingredient Name(s) - one per line", placeholder="e.g.\nTomato\nOnion")
        with cols[1]:
            ingredient_quantities = st.text_area("Quantity (match order)", placeholder="e.g.\n2\n1")
        with cols[2]:
            ingredient_units = st.text_area("Unit (match order)", placeholder="e.g.\npcs\nkg")

        st.markdown("### ⏱ Time")
        col1, col2 = st.columns(2)
        prep_time = col1.number_input("Prep Time (minutes)", min_value=0, step=1)
        cook_time = col2.number_input("Cook Time (minutes)", min_value=0, step=1)

        st.markdown("### 🧑‍🍳 Instructions")
        instructions = st.text_area("Instructions", height=150, placeholder="Step-by-step...")

        meal_type = st.selectbox("🍴 Meal Type", ["unspecified", "breakfast", "lunch", "dinner", "snack", "dessert"])

        submitted = st.form_submit_button("Save Recipe")

        if submitted and title and ingredient_names and ingredient_quantities and instructions:
            # Process ingredients into list of formatted strings
            name_lines = ingredient_names.strip().split("\n")
            qty_lines = ingredient_quantities.strip().split("\n")
            unit_lines = ingredient_units.strip().split("\n")

            ingredients_formatted = []
            ingredient_names_cleaned = []

            for i in range(len(name_lines)):
                name = name_lines[i].strip().capitalize()
                qty = qty_lines[i].strip() if i < len(qty_lines) else "1"
                unit = unit_lines[i].strip() if i < len(unit_lines) else ""
                ingredients_formatted.append(f"{qty} {unit} {name}".strip())
                ingredient_names_cleaned.append(name.lower())

            recipe = {
                "id": f"custom_{len(recipes)}",
                "title": title.strip().capitalize(),
                "image": "",
                "ingredients": ingredients_formatted,
                "ingredient_names": ingredient_names_cleaned,
                "instructions": instructions,
                "prep_time": prep_time,
                "cook_time": cook_time,
                "meal_type": meal_type,
                "source": "custom"
            }

            recipe_book.save_recipe(recipe)
            st.success("✅ Recipe added to your book!")
            st.rerun()

# --- Recipe Book ---
st.subheader("📚 Saved Recipes")

if not recipes:
    st.info("No recipes saved yet.")
else:
    for recipe in recipes:
        with st.container():
            col1, col2 = st.columns([6, 1])
            col1.markdown(f"### {recipe['title']}")
            if col2.button("❌", key=f"remove_{recipe['id']}"):
                recipe_book.remove_recipe(recipe["id"])
                st.rerun()

            with st.expander("📋 View Recipe"):
                if recipe["image"]:
                    st.image(recipe["image"], width=300)

                st.markdown("#### 📝 Ingredients")
                for line in recipe["ingredients"]:
                    st.markdown(f"- {line}")

                st.markdown("#### ⏱ Time")
                st.markdown(f"Prep: **{recipe.get('prep_time', 0)}** min | Cook: **{recipe.get('cook_time', 0)}** min")

                st.markdown("#### 🧑‍🍳 Instructions")
                st.markdown(recipe["instructions"], unsafe_allow_html=True)

                col3, col4 = st.columns(2)
                if col3.button("🛒 Plan Meal", key=f"plan_{recipe['id']}"):
                    recipe_book.plan_meal(recipe["id"])
                    st.success("Added missing ingredients to shopping cart.")