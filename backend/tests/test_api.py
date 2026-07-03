"""
Tests for the Flask API endpoints (GET, POST, PATCH, DELETE).

These use Flask's test client, so no real server is needed.
The external OpenFoodFacts calls are replaced with mocks.
"""

from unittest.mock import patch

import database


# ---------- GET /inventory ----------

def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 5
    assert items[0]["product_name"] == "Organic Almond Milk"


# ---------- GET /inventory/<id> ----------

def test_get_one_item(client):
    response = client.get("/inventory/2")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Rice Noodles"


def test_get_missing_item_returns_404(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ---------- POST /inventory ----------

def test_add_item(client):
    new_item = {"product_name": "Oat Milk", "brands": "Oatly", "price": 4.5, "stock": 10}
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201

    created = response.get_json()
    assert created["product_name"] == "Oat Milk"
    assert created["id"] == 6  # next id after the 5 starting items
    assert len(database.inventory) == 6


def test_add_item_without_name_fails(client):
    response = client.post("/inventory", json={"brands": "NoName"})
    assert response.status_code == 400
    assert len(database.inventory) == 5  # nothing was added


# ---------- PATCH /inventory/<id> ----------

def test_update_price_and_stock(client):
    response = client.patch("/inventory/1", json={"price": 4.25, "stock": 35})
    assert response.status_code == 200

    updated = response.get_json()
    assert updated["price"] == 4.25
    assert updated["stock"] == 35
    assert updated["product_name"] == "Organic Almond Milk"  # unchanged


def test_update_cannot_change_id(client):
    response = client.patch("/inventory/1", json={"id": 999, "price": 5.0})
    assert response.status_code == 200
    assert response.get_json()["id"] == 1  # id stayed the same


def test_update_missing_item_returns_404(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404


def test_update_with_no_data_fails(client):
    response = client.patch("/inventory/1", json={})
    assert response.status_code == 400


# ---------- DELETE /inventory/<id> ----------

def test_delete_item(client):
    response = client.delete("/inventory/3")
    assert response.status_code == 200
    assert len(database.inventory) == 4
    assert database.find_item(3) is None


def test_delete_missing_item_returns_404(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


# ---------- External API routes (OpenFoodFacts mocked) ----------

FAKE_PRODUCT = {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "categories": "Spreads",
    "ingredients_text": "Sugar, palm oil, hazelnuts",
    "nutriscore_grade": "e",
    "image_url": "http://example.com/nutella.jpg",
    "barcode": "3017620422003",
}


@patch("openfoodfacts.fetch_product_by_barcode", return_value=FAKE_PRODUCT)
def test_external_product_lookup(mock_fetch, client):
    response = client.get("/external/product/3017620422003")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"
    mock_fetch.assert_called_once_with("3017620422003")


@patch("openfoodfacts.fetch_product_by_barcode", return_value=None)
def test_external_product_not_found(mock_fetch, client):
    response = client.get("/external/product/0000000000000")
    assert response.status_code == 404


@patch("openfoodfacts.search_products_by_name", return_value=[FAKE_PRODUCT])
def test_external_search(mock_search, client):
    response = client.get("/external/search?name=nutella")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_external_search_without_name_fails(client):
    response = client.get("/external/search")
    assert response.status_code == 400


@patch("openfoodfacts.fetch_product_by_barcode", return_value=FAKE_PRODUCT)
def test_enhance_item_fills_empty_fields(mock_fetch, client):
    # Item 3 (Nutella) starts with an empty image_url.
    response = client.post("/inventory/3/enhance")
    assert response.status_code == 200

    enhanced = response.get_json()
    assert enhanced["image_url"] == "http://example.com/nutella.jpg"
    # Existing data must NOT be overwritten.
    assert enhanced["ingredients_text"] == "Sugar, palm oil, hazelnuts, cocoa, skimmed milk powder"


def test_enhance_item_without_barcode_fails(client):
    # Add an item that has no barcode, then try to enhance it.
    response = client.post("/inventory", json={"product_name": "Mystery Snack"})
    new_id = response.get_json()["id"]

    response = client.post(f"/inventory/{new_id}/enhance")
    assert response.status_code == 400
