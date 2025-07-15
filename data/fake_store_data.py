import pandas as pd
import random

def get_store_prices():
    categories = {
        "vegetable": ["tomato", "onion", "garlic", "carrot", "lettuce", "spinach", "pepper", "cucumber", "zucchini", "broccoli"],
        "fruit": ["apple", "banana", "orange", "grape", "pear", "peach", "mango", "pineapple", "strawberry", "blueberry"],
        "meat": ["chicken", "beef", "pork", "lamb", "turkey", "sausage", "bacon", "ham", "duck", "veal"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "egg", "ice cream", "sour cream", "mozzarella", "parmesan"],
        "grain": ["rice", "pasta", "bread", "flour", "oats", "cornmeal", "cereal", "quinoa", "barley", "couscous"],
        "spice": ["salt", "pepper", "cumin", "cinnamon", "basil", "oregano", "paprika", "turmeric", "chili powder", "thyme"],
        "condiment": ["ketchup", "mustard", "mayonnaise", "soy sauce", "vinegar", "honey", "maple syrup", "hot sauce", "bbq sauce", "jam"],
        "canned": ["beans", "corn", "peas", "tomato sauce", "tuna", "chickpeas", "coconut milk", "pineapple chunks", "olives", "mushrooms"]
    }

    ingredients = []
    for category, items in categories.items():
        for item in items:
            ingredients.append((item, category))

    extra_names = ["organic", "fresh", "dried", "chopped", "sliced", "grated"]
    for _ in range(430):  # total ~500
        base_item, category = random.choice(ingredients)
        variation = random.choice(extra_names)
        new_item = f"{variation} {base_item}"
        ingredients.append((new_item, category))

    store_data = []
    stores = ["Walmart", "Target", "Whole Foods"]

    for ingredient, category in ingredients:
        base_price = round(random.uniform(0.3, 10.0), 2)
        prices = {
            "Walmart": round(base_price * random.uniform(0.9, 1.1), 2),
            "Target": round(base_price * random.uniform(0.9, 1.1), 2),
            "Whole Foods": round(base_price * random.uniform(0.9, 1.2), 2),
        }

        sale_store = random.choice(stores)
        discount_percent = random.choice([0, 10, 15, 20, 25, 30])
        if discount_percent > 0:
            prices[sale_store] = round(prices[sale_store] * (1 - discount_percent / 100), 2)

        store_data.append({
            "Ingredient": ingredient,
            "Category": category,
            "Walmart": prices["Walmart"],
            "Target": prices["Target"],
            "Whole Foods": prices["Whole Foods"],
            "On Sale": sale_store if discount_percent > 0 else "",
            "Discount": f"{discount_percent}%" if discount_percent > 0 else ""
        })

    return pd.DataFrame(store_data)