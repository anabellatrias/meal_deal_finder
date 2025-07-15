import streamlit as st
from services.shopping_cart import ShoppingCart

st.set_page_config(page_title="Shopping Cart", layout="centered")

st.title("🛒 Shopping Cart")
cart = ShoppingCart(st.session_state)
cart_items = cart.get_cart()

colA = st.columns(1)
if colA[0].button("🧹 Clear Cart"):
    cart.clear_cart()
    st.success("Cart cleared.")
    st.rerun()

# --- Add Custom Item Form ---
with st.expander("➕ Add Custom Item"):
    with st.form("add_cart_item"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Item Name", placeholder="e.g. Tomato")
        quantity = col2.number_input("Quantity", min_value=0.0, value=1.0)

        col3, col4 = st.columns(2)
        unit = col3.selectbox("Unit", ["pcs", "g", "kg", "ml", "l", "oz", "lb"])
        category = col4.text_input("Category (optional)", placeholder="e.g. Vegetable")

        add_submitted = st.form_submit_button("Add to Cart")

        if add_submitted and name:
            cart.add_item(name=name, quantity=quantity, unit=unit, category=category or "Misc")
            st.success(f"{name.capitalize()} added to cart.")
            st.rerun()

# --- Display Cart Table ---
st.subheader("📦 Cart Items")

if cart_items.empty:
    st.info("Your cart is empty. Add items manually or from recipes.")
else:
    for idx, row in cart_items.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        col1.markdown(f"**{row['Item Name']}**")
        col2.markdown(f"{row['Quantity']} {row['Unit']}")
        col3.markdown(f"{row['Category']}")
        col4.empty()
        if col5.button("❌", key=f"remove_{idx}"):
            cart.remove_item(idx)
            st.rerun()

# --- Price Comparison ---
st.subheader("💰 Price Comparison")
price_df = cart.get_price_comparison()

if not price_df.empty:
    price_df_display = price_df.sort_values("Best Price", na_position="last").reset_index(drop=True)
    st.dataframe(price_df_display[[
        "Item Name", "Quantity", "Unit", "Category",
        "Walmart", "Target", "Whole Foods", "Cheapest Store", "Best Price", "💸 Deal"
    ]], use_container_width=True)

    total = price_df_display["Best Price"].sum()
    store_totals = {}
    for store in ["Walmart", "Target", "Whole Foods"]:
        store_totals[store] = price_df_display[store].sum()

    # Find best total
    best_store = min(store_totals, key=store_totals.get)
    best_total = store_totals[best_store]

    # Display all totals
    st.markdown("### 🛍️ Store Totals")
    for store, total_price in store_totals.items():
        if store == best_store:
            st.success(f"✅ {store}: **${total_price:.2f}** (Best)")
        else:
            st.markdown(f"- {store}: ${total_price:.2f}")
    st.success(f"🧾 Total Estimated Cost: **${total:.2f}**")
else:
    st.warning("No store pricing available for the current items.")