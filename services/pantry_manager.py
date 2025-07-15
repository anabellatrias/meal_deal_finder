import pandas as pd
import os
import json

# Paths for saving pantry and buy again lists
PANTRY_FILE = "data/pantry.json"
BUY_AGAIN_FILE = "data/buy_again.json"

def save_df_to_json(df, path):
    df.to_json(path, orient="records", indent=2)

def load_df_from_json(path, columns):
    if os.path.exists(path):
        try:
            return pd.read_json(path)
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

class PantryManager:
    def __init__(self, session_state):
        self.session_state = session_state

        if 'pantry' not in self.session_state:
            self.session_state.pantry = load_df_from_json(PANTRY_FILE, [
                'Item Name', 'Category', 'Quantity', 'Unit', 'Restock Status'
            ])

        if 'buy_again' not in self.session_state:
            self.session_state.buy_again = load_df_from_json(BUY_AGAIN_FILE, [
                'Item Name', 'Category', 'Quantity', 'Unit'
            ])

    def get_pantry(self):
        return self.session_state.pantry

    def get_buy_again(self):
        return self.session_state.buy_again

    def add_or_edit_ingredient(self, name, category, quantity, unit, restock_status):
        name = name.strip().capitalize()
        category = category.capitalize()
        unit = unit.lower()

        df = self.session_state.pantry
        if name in df['Item Name'].values:
            return "duplicate"

        new_row = pd.DataFrame([{
            'Item Name': name,
            'Category': category,
            'Quantity': quantity,
            'Unit': unit,
            'Restock Status': restock_status
        }])
        self.session_state.pantry = pd.concat([df, new_row], ignore_index=True)
        save_df_to_json(self.session_state.pantry, PANTRY_FILE)
        return "added"

    def remove_ingredient(self, index):
        self.session_state.pantry = self.session_state.pantry.drop(index).reset_index(drop=True)
        save_df_to_json(self.session_state.pantry, PANTRY_FILE)

    def move_to_buy_again(self, index):
        row = self.session_state.pantry.loc[index]
        new_row = pd.DataFrame([{
            'Item Name': row['Item Name'],
            'Category': row['Category'],
            'Quantity': row['Quantity'],
            'Unit': row['Unit']
        }])
        self.session_state.buy_again = pd.concat(
            [self.session_state.buy_again, new_row], ignore_index=True
        )
        self.remove_ingredient(index)
        save_df_to_json(self.session_state.buy_again, BUY_AGAIN_FILE)

    def remove_from_buy_again(self, index):
        self.session_state.buy_again = self.session_state.buy_again.drop(index).reset_index(drop=True)
        save_df_to_json(self.session_state.buy_again, BUY_AGAIN_FILE)

    def update_ingredient(self, index, quantity, restock_status):
        self.session_state.pantry.at[index, 'Quantity'] = quantity
        self.session_state.pantry.at[index, 'Restock Status'] = restock_status
        save_df_to_json(self.session_state.pantry, PANTRY_FILE)

    def clear_pantry(self):
        self.session_state.pantry = pd.DataFrame(columns=[
            'Item Name', 'Category', 'Quantity', 'Unit', 'Restock Status'
        ])

    def clear_buy_again(self):
        self.session_state.buy_again = pd.DataFrame(columns=[
            'Item Name', 'Category', 'Quantity', 'Unit'
        ])