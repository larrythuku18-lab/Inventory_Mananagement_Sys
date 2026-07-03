"""
Command line tool for the inventory management system.

It talks to the Flask API over HTTP, so the Flask server must be
running first:  python app.py

Then in another terminal:  python cli.py
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

MENU = """
========= INVENTORY MANAGER =========
1. View all items
2. View one item
3. Add a new item
4. Update an item (price / stock / etc.)
5. Delete an item
6. Find a product on OpenFoodFacts
7. Enhance an item with OpenFoodFacts data
0. Exit
=====================================
"""


def print_item(item):
    """Print one inventory item in a readable way."""
    print(f"  [{item['id']}] {item['product_name']} ({item['brands']})")
    print(f"      barcode: {item['barcode'] or '-'}  |  price: {item['price']}  |  stock: {item['stock']}")


def ask_int(prompt):
    """Keep asking until the user types a whole number."""
    while True:
        text = input(prompt).strip()
        try:
            return int(text)
        except ValueError:
            print("Please enter a whole number.")


def ask_float(prompt):
    """Keep asking until the user types a number."""
    while True:
        text = input(prompt).strip()
        try:
            return float(text)
        except ValueError:
            print("Please enter a number.")


# ---------- MENU ACTIONS ----------

def view_all_items():
    """Triggered by menu option 1 -> GET /inventory"""
    response = requests.get(f"{BASE_URL}/inventory")
    items = response.json()
    if not items:
        print("Inventory is empty.")
        return
    print(f"\n{len(items)} item(s) in inventory:")
    for item in items:
        print_item(item)


def view_one_item():
    """Triggered by menu option 2 -> GET /inventory/<id>"""
    item_id = ask_int("Item id: ")
    response = requests.get(f"{BASE_URL}/inventory/{item_id}")
    if response.status_code == 404:
        print("No item with that id.")
        return
    item = response.json()
    print_item(item)
    print(f"      categories: {item['categories'] or '-'}")
    print(f"      ingredients: {item['ingredients_text'] or '-'}")
    print(f"      nutriscore: {item['nutriscore_grade'] or '-'}")


def add_item():
    """Triggered by menu option 3 -> POST /inventory"""
    name = input("Product name: ").strip()
    if not name:
        print("Product name cannot be empty.")
        return
    new_item = {
        "product_name": name,
        "brands": input("Brand (optional): ").strip(),
        "barcode": input("Barcode (optional): ").strip(),
        "price": ask_float("Price: "),
        "stock": ask_int("Stock: "),
    }
    response = requests.post(f"{BASE_URL}/inventory", json=new_item)
    if response.status_code == 201:
        print("Item added:")
        print_item(response.json())
    else:
        print("Could not add item:", response.json().get("error"))


def update_item():
    """Triggered by menu option 4 -> PATCH /inventory/<id>"""
    item_id = ask_int("Item id to update: ")
    print("Leave a field blank to keep its current value.")
    updates = {}

    price_text = input("New price: ").strip()
    if price_text:
        try:
            updates["price"] = float(price_text)
        except ValueError:
            print("Ignoring invalid price.")

    stock_text = input("New stock: ").strip()
    if stock_text:
        try:
            updates["stock"] = int(stock_text)
        except ValueError:
            print("Ignoring invalid stock.")

    name_text = input("New product name: ").strip()
    if name_text:
        updates["product_name"] = name_text

    if not updates:
        print("Nothing to update.")
        return

    response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=updates)
    if response.status_code == 200:
        print("Item updated:")
        print_item(response.json())
    else:
        print("Could not update:", response.json().get("error"))


def delete_item():
    """Triggered by menu option 5 -> DELETE /inventory/<id>"""
    item_id = ask_int("Item id to delete: ")
    confirm = input(f"Really delete item {item_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return
    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    if response.status_code == 200:
        print("Item deleted.")
    else:
        print("Could not delete:", response.json().get("error"))


def find_on_openfoodfacts():
    """Triggered by menu option 6 -> GET /external/product/<barcode>
    or GET /external/search?name=..."""
    choice = input("Search by (b)arcode or (n)ame? ").strip().lower()

    if choice == "b":
        barcode = input("Barcode: ").strip()
        response = requests.get(f"{BASE_URL}/external/product/{barcode}")
        if response.status_code != 200:
            print("Not found:", response.json().get("error"))
            return
        product = response.json()
        print(f"  {product['product_name']} ({product['brands']})")
        print(f"  ingredients: {product['ingredients_text'] or '-'}")
        print(f"  nutriscore: {product['nutriscore_grade'] or '-'}")

    elif choice == "n":
        name = input("Product name: ").strip()
        response = requests.get(f"{BASE_URL}/external/search", params={"name": name})
        if response.status_code != 200:
            print("Search failed:", response.json().get("error"))
            return
        results = response.json()
        if not results:
            print("No products found.")
            return
        print(f"Found {len(results)} product(s):")
        for product in results:
            print(f"  {product['product_name']} ({product['brands']}) barcode: {product['barcode']}")

    else:
        print("Please choose 'b' or 'n'.")


def enhance_item():
    """Triggered by menu option 7 -> POST /inventory/<id>/enhance"""
    item_id = ask_int("Item id to enhance: ")
    response = requests.post(f"{BASE_URL}/inventory/{item_id}/enhance")
    if response.status_code == 200:
        print("Item enhanced with OpenFoodFacts data:")
        item = response.json()
        print_item(item)
        print(f"      categories: {item['categories'] or '-'}")
        print(f"      ingredients: {item['ingredients_text'] or '-'}")
    else:
        print("Could not enhance:", response.json().get("error"))


def main():
    """Show the menu in a loop until the user exits."""
    actions = {
        "1": view_all_items,
        "2": view_one_item,
        "3": add_item,
        "4": update_item,
        "5": delete_item,
        "6": find_on_openfoodfacts,
        "7": enhance_item,
    }

    print("Welcome to the Inventory Manager CLI!")
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid option, please choose 0-7.")
            continue

        try:
            action()
        except requests.ConnectionError:
            print("ERROR: Cannot reach the API. Is the Flask server running?")
        except requests.RequestException as error:
            print("ERROR: API request failed:", error)


if __name__ == "__main__":
    main()
