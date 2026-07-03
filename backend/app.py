

from flask import Flask, jsonify, request
from flask_cors import CORS

import database
import openfoodfacts

app = Flask(__name__)
CORS(app)  # allow the React frontend to call this API


# ---------- READ ROUTES ----------

@app.route("/inventory", methods=["GET"])
def get_all_items():
    """Return the whole inventory list."""
    return jsonify(database.inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    """Return a single item by its id, or a 404 error."""
    item = database.find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


# ---------- CREATE ROUTE ----------

@app.route("/inventory", methods=["POST"])
def add_item():
    """Add a new item to the inventory.

    Expects a JSON body with at least "product_name".
    All other fields are optional and get sensible defaults.
    """
    data = request.get_json(silent=True)
    if not data or not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": database.get_next_id(),
        "barcode": data.get("barcode", ""),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "categories": data.get("categories", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "nutriscore_grade": data.get("nutriscore_grade", ""),
        "image_url": data.get("image_url", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
    }
    database.inventory.append(new_item)
    return jsonify(new_item), 201


# ---------- UPDATE ROUTE ----------

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    """Update one or more fields on an existing item.

    Expects a JSON body with the fields to change,
    e.g. {"price": 4.50, "stock": 30}.
    """
    item = database.find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Only allow known fields to be updated (never the id).
    allowed_fields = [
        "barcode", "product_name", "brands", "categories",
        "ingredients_text", "nutriscore_grade", "image_url",
        "price", "stock",
    ]
    for field in allowed_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


# ---------- DELETE ROUTE ----------

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Remove an item from the inventory."""
    item = database.find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    database.inventory.remove(item)
    return jsonify({"message": "Item deleted", "id": item_id}), 200


# ---------- EXTERNAL API ROUTES ----------

@app.route("/external/product/<barcode>", methods=["GET"])
def external_product(barcode):
    """Look up a product on OpenFoodFacts by barcode."""
    product = openfoodfacts.fetch_product_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    return jsonify(product), 200


@app.route("/external/search", methods=["GET"])
def external_search():
    """Search OpenFoodFacts by product name (?name=...)."""
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "name query parameter is required"}), 400

    results = openfoodfacts.search_products_by_name(name)
    if results is None:
        return jsonify({"error": "OpenFoodFacts API request failed"}), 502
    return jsonify(results), 200


@app.route("/inventory/<int:item_id>/enhance", methods=["POST"])
def enhance_item(item_id):
    """Fill in missing details on an item using OpenFoodFacts.

    The item must have a barcode. Only empty fields are filled,
    so data typed in by employees is never overwritten.
    """
    item = database.find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    if not item.get("barcode"):
        return jsonify({"error": "Item has no barcode to look up"}), 400

    product = openfoodfacts.fetch_product_by_barcode(item["barcode"])
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    for field, value in product.items():
        if field != "barcode" and not item.get(field):
            item[field] = value

    return jsonify(item), 200


if __name__ == "__main__":
    app.run(debug=True)
