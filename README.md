# 🥘 Meal Deal Finder

Meal Deal Finder is an all-in-one platform designed to make meal planning smarter, faster, and more affordable. Built with Python and Streamlit, the app combines pantry tracking, recipe generation, and real-time grocery price comparison to help users reduce food waste, save money, and plan meals based on what they already have at home.

---

## 📌 Features

- **Pantry Management**: Add, edit, and restock ingredients organized by category, unit, and quantity.
- **Recipe Generator**: Get meal suggestions based on pantry ingredients, diet, and allergy filters.
- **Recipe Book**: Save your favorite or custom recipes and use them for weekly meal planning.
- **Shopping Cart**: Automatically generates a list of missing ingredients and compares prices across stores.
- **Price Comparison**: Estimate grocery costs at Walmart, Target, and Whole Foods to find the cheapest option.

---

## 🛠️ Tech Stack

- **Language**: Python
- **Framework**: Streamlit
- **Data Handling**: pandas
- **API**: [Spoonacular API](https://spoonacular.com/food-api) (for recipe generation)

---

## 📂 Project Structure

- `pages/` – Multi-page Streamlit components (Pantry, Cart, Recipes, etc.)
- `services/` – Logic for managing pantry items, cart operations, and price estimates
- `main.py` – App launcher
