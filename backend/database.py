"""
Mock database for the inventory system.

This simulates data storage using a simple Python list.
Each item is a dictionary shaped like a product from the
OpenFoodFacts API, plus two store-specific fields we need
for inventory management: "price" and "stock".
Every item has a unique "id".
"""

# The mock database: a list of product dictionaries.
inventory = [
    {
        "id": 1,
        "barcode": "025293600881",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "categories": "Beverages, Plant-based milks",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, natural flavor",
        "nutriscore_grade": "b",
        "image_url": "",
        "price": 3.99,
        "stock": 40,
    },
    {
        "id": 2,
        "barcode": "737628064502",
        "product_name": "Rice Noodles",
        "brands": "Thai Kitchen",
        "categories": "Pastas, Noodles",
        "ingredients_text": "Rice flour, water",
        "nutriscore_grade": "a",
        "image_url": "",
        "price": 2.49,
        "stock": 75,
    },
    {
        "id": 3,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "categories": "Spreads, Hazelnut spreads",
        "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa, skimmed milk powder",
        "nutriscore_grade": "e",
        "image_url": "",
        "price": 4.99,
        "stock": 25,
    },
    {
        "id": 4,
        "barcode": "038000138416",
        "product_name": "Corn Flakes",
        "brands": "Kellogg's",
        "categories": "Breakfast cereals",
        "ingredients_text": "Milled corn, sugar, malt flavor, salt",
        "nutriscore_grade": "c",
        "image_url": "",
        "price": 3.29,
        "stock": 60,
    },
    {
        "id": 5,
        "barcode": "5449000000996",
        "product_name": "Coca-Cola",
        "brands": "Coca-Cola",
        "categories": "Beverages, Sodas",
        "ingredients_text": "Carbonated water, sugar, caramel color, phosphoric acid, caffeine",
        "nutriscore_grade": "e",
        "image_url": "",
        "price": 1.99,
        "stock": 120,
    },
]


def get_next_id():
    """Return the next free id (highest existing id + 1)."""
    if not inventory:
        return 1
    return max(item["id"] for item in inventory) + 1


def find_item(item_id):
    """Return the item with the given id, or None if it does not exist."""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None
