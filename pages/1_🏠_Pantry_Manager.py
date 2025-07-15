import streamlit as st
from services.pantry_manager import PantryManager

st.set_page_config(page_title="Pantry Manager", layout="centered")

pantry_manager = PantryManager(st.session_state)
df = pantry_manager.get_pantry()
buy_again_df = pantry_manager.get_buy_again()

category_emojis = {
    "Vegetable": "🥦",
    "Fruit": "🍎",
    "Meat": "🍖",
    "Dairy": "🧀",
    "Grain": "🌾",
    "Spice": "🧂",
    "Condiment": "🍯",
    "Canned": "🥫"
}

categories = list(category_emojis.keys())
units = ["g", "kg", "ml", "l", "pcs", "oz", "lb"]
restock_options = ["In Stock", "Buy Again"]

st.title("🏠 Pantry Manager")

# --- Add Ingredient Form ---
with st.expander("➕ Add Ingredient"):
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Item Name")
        category = col2.selectbox("Category", categories)
        col3, col4 = st.columns(2)
        quantity = col3.number_input("Quantity", min_value=0.0, format="%.2f")
        unit = col4.selectbox("Unit", units)
        restock_status = st.selectbox("Restock Status", restock_options)
        submitted = st.form_submit_button("Add to Pantry")
        if submitted and name:
            result = pantry_manager.add_or_edit_ingredient(name, category, quantity, unit, restock_status)
            if result == "duplicate":
                st.warning("This item already exists. Edit it below instead.")
            else:
                st.success(f"{name.capitalize()} added to pantry.")
                st.rerun()

# --- Pantry Display ---
st.subheader("Your Pantry")

if df.empty:
    st.info("Your pantry is empty.")
else:
    if "editing_idx" not in st.session_state:
        st.session_state.editing_idx = None

    for cat in sorted(df['Category'].unique()):
        emoji = category_emojis.get(cat, "📦")
        st.markdown(f"### {emoji} {cat}")
        cat_df = df[df['Category'] == cat].reset_index(drop=True)
        for local_idx, row in cat_df.iterrows():
            global_idx = df[(df['Category'] == cat)].index[local_idx]
            editing = st.session_state.editing_idx == global_idx

            if editing:
                with st.form(f"edit_form_{global_idx}"):
                    col1, col2 = st.columns(2)
                    quantity = col1.number_input("Quantity", value=float(row['Quantity']), min_value=0.0, format="%.2f")
                    restock_status = col2.selectbox("Restock Status", restock_options, index=restock_options.index(row["Restock Status"]))
                    save = st.form_submit_button("Save")
                    cancel = st.form_submit_button("Cancel")

                    if save:
                        pantry_manager.update_ingredient(global_idx, quantity, restock_status)
                        st.session_state.editing_idx = None
                        st.success("Ingredient updated.")
                        st.rerun()
                    elif cancel:
                        st.session_state.editing_idx = None
                        st.rerun()
            else:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 1, 1, 1])
                col1.markdown(f"**{row['Item Name']}**")
                col2.markdown(f"{row['Quantity']} {row['Unit']}")
                col3.markdown(f"{row['Restock Status']}")
                if col4.button("🔁", key=f"restock_{cat}_{local_idx}"):
                    pantry_manager.move_to_buy_again(global_idx)
                    st.rerun()
                if col5.button("✏️", key=f"edit_{cat}_{local_idx}"):
                    st.session_state.editing_idx = global_idx
                    st.rerun()
                if col6.button("❌", key=f"delete_{cat}_{local_idx}"):
                    pantry_manager.remove_ingredient(global_idx)
                    st.rerun()

# --- Buy Again Section ---
st.subheader("🛒 Buy Again")

if buy_again_df.empty:
    st.info("No ingredients to buy again.")
else:
    for cat in sorted(buy_again_df['Category'].unique()):
        emoji = category_emojis.get(cat, "🛍️")
        st.markdown(f"### {emoji} {cat}")
        cat_df = buy_again_df[buy_again_df['Category'] == cat].reset_index(drop=True)
        for local_idx, row in cat_df.iterrows():
            global_idx = buy_again_df[(buy_again_df['Category'] == cat)].index[local_idx]
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{row['Item Name']}**")
            col2.markdown(f"{row['Quantity']} {row['Unit']}")
            col3.markdown(f"{row['Category']}")
            if col4.button("❌", key=f"remove_buy_{cat}_{local_idx}"):
                pantry_manager.remove_from_buy_again(global_idx)
                st.rerun()