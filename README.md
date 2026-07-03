# Inventory Management System

A simple inventory management system for a small retail company.
Employees can **add, view, update and delete** inventory items, and the
system can pull real product details from the **OpenFoodFacts API**.

| Part     | Tech                          |
| -------- | ----------------------------- |
| Backend  | Flask (Python) REST API       |
| Frontend | React (Vite) admin portal     |
| CLI      | Python menu tool over the API |
| Tests    | pytest + unittest.mock        |
| Storage  | In-memory Python list (mock)  |

---

## Project structure

```
Inventory_Management_Sys/
├── backend/
│   ├── app.py             # Flask app + all routes
│   ├── database.py        # mock database (list of dicts)
│   ├── openfoodfacts.py   # OpenFoodFacts API client
│   ├── cli.py             # command line tool
│   ├── requirements.txt
│   └── tests/             # pytest test suite
└── frontend/              # React admin portal
```

## Installation & setup

### 1. Backend (Flask)

```bash
cd Inventory_Management_Sys
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python app.py                     # starts on http://127.0.0.1:5000 (debug mode)
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev                       # opens on http://localhost:5173
```

### 3. CLI (needs the Flask server running)

```bash
cd backend
python cli.py
```

### 4. Run the tests

```bash
./venv/bin/python -m pytest backend/tests/ -v
```

---

## Route plan (API design)

Every route was planned with its **inputs**, its **output**, **what it
changes** in the data, and **when the CLI triggers it**.

### Inventory CRUD routes

| Route | Method | Inputs | Output | Data change | CLI trigger |
| ----- | ------ | ------ | ------ | ----------- | ----------- |
| `/inventory` | GET | none | `200` + JSON list of all items | none (read only) | Menu option **1** – View all items |
| `/inventory/<id>` | GET | `id` in URL | `200` + item, or `404` | none (read only) | Menu option **2** – View one item |
| `/inventory` | POST | JSON body, `product_name` required (`brands`, `barcode`, `price`, `stock`… optional) | `201` + created item with new `id`, or `400` | **appends** a new dict to the array | Menu option **3** – Add a new item |
| `/inventory/<id>` | PATCH | `id` in URL + JSON body of fields to change, e.g. `{"price": 4.5, "stock": 30}` | `200` + updated item, `404` or `400` | **updates** fields on one dict (never the `id`) | Menu option **4** – Update an item |
| `/inventory/<id>` | DELETE | `id` in URL | `200` + confirmation, or `404` | **removes** one dict from the array | Menu option **5** – Delete an item |

### External API routes (OpenFoodFacts)

| Route | Method | Inputs | Output | Data change | CLI trigger |
| ----- | ------ | ------ | ------ | ----------- | ----------- |
| `/external/product/<barcode>` | GET | `barcode` in URL | `200` + product data, or `404` | none | Menu option **6** (barcode search) |
| `/external/search?name=...` | GET | `name` query param | `200` + list of matches, `400` or `502` | none | Menu option **6** (name search) |
| `/inventory/<id>/enhance` | POST | `id` in URL (item must have a barcode) | `200` + enhanced item, `404` or `400` | **fills empty fields** on one dict with API data (never overwrites) | Menu option **7** – Enhance an item |

### Mock database shape

Each item in the array mirrors what OpenFoodFacts returns, plus store
fields (`price`, `stock`) and a unique `id`:

```json
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
  "stock": 40
}
```

---

## Example API usage (curl / Postman)

```bash
# All items
curl http://127.0.0.1:5000/inventory

# One item
curl http://127.0.0.1:5000/inventory/1

# Add an item
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Oat Milk", "brands": "Oatly", "price": 4.5, "stock": 12}'

# Update price and stock
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 4.25, "stock": 35}'

# Delete an item
curl -X DELETE http://127.0.0.1:5000/inventory/2

# Look up a real product on OpenFoodFacts by barcode
curl http://127.0.0.1:5000/external/product/3017620422003

# Search OpenFoodFacts by name
curl "http://127.0.0.1:5000/external/search?name=nutella"

# Fill in missing fields on item 3 from OpenFoodFacts
curl -X POST http://127.0.0.1:5000/inventory/3/enhance
```

## Example CLI session

```
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

Choose an option: 3
Product name: Oat Milk
Brand (optional): Oatly
Barcode (optional): 7394376616501
Price: 4.50
Stock: 12
Item added:
  [6] Oat Milk (Oatly)
      barcode: 7394376616501  |  price: 4.5  |  stock: 12
```

The CLI validates every input (retries on bad numbers) and prints a
friendly error if the Flask server is not running or the external API
fails.

## Error handling

- `400` – missing/invalid request data (e.g. no `product_name`)
- `404` – item or product not found
- `502` – OpenFoodFacts request failed
- The OpenFoodFacts client catches timeouts and network errors and
  returns `None` instead of crashing.

## Tests

34 tests cover:

- every API endpoint (GET, POST, PATCH, DELETE, external routes)
- the OpenFoodFacts client (success, not-found, network failure)
- the CLI commands (mocked `requests` and mocked `input()`)

All external calls are mocked with `unittest.mock`, so the suite runs
offline in under a second.
