"""
Functions that talk to the real OpenFoodFacts API.

Docs: https://world.openfoodfacts.org/data
- Fetch by barcode: https://world.openfoodfacts.org/api/v2/product/<barcode>.json
- Search by name:   https://world.openfoodfacts.org/cgi/search.pl
"""

import requests

PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# Be polite: OpenFoodFacts asks apps to identify themselves.
HEADERS = {"User-Agent": "InventoryManagementSys - learning project"}

# Only keep the fields our inventory actually uses.
FIELDS_WE_WANT = [
    "product_name", "brands", "categories",
    "ingredients_text", "nutriscore_grade", "image_url",
]


def _pick_fields(product):
    """Copy only the fields we care about out of a raw API product dict."""
    picked = {}
    for field in FIELDS_WE_WANT:
        picked[field] = product.get(field, "")
    return picked


def fetch_product_by_barcode(barcode):
    """Look up one product on OpenFoodFacts by its barcode.

    Returns a dict with our chosen fields (plus the barcode),
    or None if the product was not found or the API failed.
    """
    try:
        response = requests.get(
            PRODUCT_URL.format(barcode=barcode), headers=HEADERS, timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        # Network problem, timeout, or bad status code.
        return None

    # OpenFoodFacts uses status 1 = found, 0 = not found.
    if data.get("status") != 1:
        return None

    result = _pick_fields(data.get("product", {}))
    result["barcode"] = barcode
    return result


def search_products_by_name(name, limit=5):
    """Search OpenFoodFacts for products matching a name.

    Returns a list of product dicts (possibly empty),
    or None if the API request failed.
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
    }
    try:
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    results = []
    for product in data.get("products", []):
        item = _pick_fields(product)
        item["barcode"] = product.get("code", "")
        results.append(item)
    return results
