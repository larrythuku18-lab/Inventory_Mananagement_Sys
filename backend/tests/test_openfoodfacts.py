"""
Tests for the OpenFoodFacts client module.

All network calls are faked with unittest.mock so the tests
run offline and never hit the real API.
"""

from unittest.mock import MagicMock, patch

import requests

import openfoodfacts


def make_fake_response(json_data):
    """Build a fake requests response object."""
    fake = MagicMock()
    fake.json.return_value = json_data
    fake.raise_for_status.return_value = None
    return fake


# ---------- fetch_product_by_barcode ----------

@patch("openfoodfacts.requests.get")
def test_fetch_product_found(mock_get):
    mock_get.return_value = make_fake_response({
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
        },
    })

    product = openfoodfacts.fetch_product_by_barcode("025293600881")

    assert product["product_name"] == "Organic Almond Milk"
    assert product["brands"] == "Silk"
    assert product["barcode"] == "025293600881"
    # Fields missing from the API answer default to empty strings.
    assert product["nutriscore_grade"] == ""


@patch("openfoodfacts.requests.get")
def test_fetch_product_not_found(mock_get):
    mock_get.return_value = make_fake_response({"status": 0})
    assert openfoodfacts.fetch_product_by_barcode("0000000000000") is None


@patch("openfoodfacts.requests.get", side_effect=requests.ConnectionError)
def test_fetch_product_network_error(mock_get):
    assert openfoodfacts.fetch_product_by_barcode("025293600881") is None


# ---------- search_products_by_name ----------

@patch("openfoodfacts.requests.get")
def test_search_products(mock_get):
    mock_get.return_value = make_fake_response({
        "products": [
            {"product_name": "Nutella", "brands": "Ferrero", "code": "3017620422003"},
            {"product_name": "Nutella B-ready", "brands": "Ferrero", "code": "8000500242322"},
        ]
    })

    results = openfoodfacts.search_products_by_name("nutella")

    assert len(results) == 2
    assert results[0]["product_name"] == "Nutella"
    assert results[0]["barcode"] == "3017620422003"


@patch("openfoodfacts.requests.get")
def test_search_no_results(mock_get):
    mock_get.return_value = make_fake_response({"products": []})
    assert openfoodfacts.search_products_by_name("zzzzzz") == []


@patch("openfoodfacts.requests.get", side_effect=requests.Timeout)
def test_search_network_error(mock_get):
    assert openfoodfacts.search_products_by_name("nutella") is None
