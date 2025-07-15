import pandas as pd
from data.fake_store_data import get_store_prices
from rapidfuzz import process


class ShoppingCart:
    def __init__(self, session_state):
        self.session_state = session_state
        if "shopping_cart" not in self.session_state:
            self.session_state.shopping_cart = pd.DataFrame(columns=[
                "Item Name", "Quantity", "Unit", "Category"
            ])

    def clear_cart(self):
        self.session_state.shopping_cart = pd.DataFrame(columns=[
            "Item Name", "Quantity", "Unit", "Category"
        ])

    def add_item(self, name, quantity=1, unit="pcs", category="Misc"):
        name = name.strip().capitalize()
        unit = unit.strip()
        category = category.strip().capitalize()

        # Check for existing entry (same name + unit)
        existing = self.session_state.shopping_cart[
            (self.session_state.shopping_cart["Item Name"] == name) &
            (self.session_state.shopping_cart["Unit"] == unit)
        ]

        if not existing.empty:
            idx = existing.index[0]
            self.session_state.shopping_cart.at[idx, "Quantity"] += quantity
        else:
            new_row = pd.DataFrame([{
                "Item Name": name,
                "Quantity": quantity,
                "Unit": unit,
                "Category": category
            }])
            self.session_state.shopping_cart = pd.concat(
                [self.session_state.shopping_cart, new_row], ignore_index=True
            )

    def add_missing_ingredients(self, names):
        for name in names:
            self.add_item(name=name, quantity=1, unit="pcs", category="Recipe")

    def remove_item(self, index):
        self.session_state.shopping_cart = self.session_state.shopping_cart.drop(index).reset_index(drop=True)

    def get_cart(self):
        return self.session_state.shopping_cart

    def get_price_comparison(self):
        cart_df = self.get_cart()
        if cart_df.empty:
            return pd.DataFrame()

        store_df = get_store_prices()
        store_df["Ingredient"] = store_df["Ingredient"].str.lower().str.strip()
        store_names = store_df["Ingredient"].tolist()

        matched_rows = []

        for _, row in cart_df.iterrows():
            cart_item = row["Item Name"].strip().lower()

            result = process.extractOne(cart_item, store_names, score_cutoff=80)

            if result:
                match, score, idx = result
                store_row = store_df.iloc[idx]
                matched_rows.append({
                    "Item Name": row["Item Name"],
                    "Quantity": row["Quantity"],
                    "Unit": row["Unit"],
                    "Category": row.get("Category", "Misc"),
                    "Walmart": store_row["Walmart"],
                    "Target": store_row["Target"],
                    "Whole Foods": store_row["Whole Foods"],
                    "Cheapest Store": None,  # Will calculate below
                    "Best Price": None,
                    "💸 Deal": f"{store_row['On Sale']} ({store_row['Discount']})" if store_row["Discount"] else ""
                })
            else:
                # No match found
                matched_rows.append({
                    "Item Name": row["Item Name"],
                    "Quantity": row["Quantity"],
                    "Unit": row["Unit"],
                    "Category": row.get("Category", "Misc"),
                    "Walmart": None,
                    "Target": None,
                    "Whole Foods": None,
                    "Cheapest Store": "N/A",
                    "Best Price": None,
                    "💸 Deal": ""
                })

        result_df = pd.DataFrame(matched_rows)

        # Determine best price and store
        for i in result_df.index:
            prices = result_df.loc[i, ["Walmart", "Target", "Whole Foods"]]
            numeric = prices.dropna()
            if not numeric.empty:
                best_store = numeric.idxmin()
                best_price = numeric.min()
                result_df.at[i, "Cheapest Store"] = best_store
                result_df.at[i, "Best Price"] = best_price

        return result_df