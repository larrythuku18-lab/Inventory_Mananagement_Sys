"""
Tests for the CLI tool.

The HTTP calls (requests) and keyboard input (input) are both
mocked, so these tests need no running server and no typing.
"""

from unittest.mock import MagicMock, patch

import cli


def make_fake_response(status_code, json_data):
    """Build a fake requests response object."""
    fake = MagicMock()
    fake.status_code = status_code
    fake.json.return_value = json_data
    return fake


FAKE_ITEM = {
    "id": 1,
    "barcode": "025293600881",
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "categories": "Beverages",
    "ingredients_text": "Filtered water, almonds",
    "nutriscore_grade": "b",
    "image_url": "",
    "price": 3.99,
    "stock": 40,
}


# ---------- input helpers ----------

@patch("builtins.input", side_effect=["abc", "12"])
def test_ask_int_retries_until_valid(mock_input):
    assert cli.ask_int("Item id: ") == 12
    assert mock_input.call_count == 2


@patch("builtins.input", side_effect=["oops", "3.5"])
def test_ask_float_retries_until_valid(mock_input):
    assert cli.ask_float("Price: ") == 3.5


# ---------- viewing ----------

@patch("cli.requests.get")
def test_view_all_items(mock_get, capsys):
    mock_get.return_value = make_fake_response(200, [FAKE_ITEM])

    cli.view_all_items()

    mock_get.assert_called_once_with(f"{cli.BASE_URL}/inventory")
    output = capsys.readouterr().out
    assert "Organic Almond Milk" in output


@patch("builtins.input", return_value="999")
@patch("cli.requests.get")
def test_view_missing_item(mock_get, mock_input, capsys):
    mock_get.return_value = make_fake_response(404, {"error": "Item not found"})

    cli.view_one_item()

    assert "No item with that id" in capsys.readouterr().out


# ---------- adding ----------

@patch("builtins.input", side_effect=["Oat Milk", "Oatly", "111222333", "4.5", "10"])
@patch("cli.requests.post")
def test_add_item_sends_correct_data(mock_post, mock_input):
    created = dict(FAKE_ITEM, product_name="Oat Milk", brands="Oatly")
    mock_post.return_value = make_fake_response(201, created)

    cli.add_item()

    sent = mock_post.call_args.kwargs["json"]
    assert sent["product_name"] == "Oat Milk"
    assert sent["price"] == 4.5
    assert sent["stock"] == 10


@patch("builtins.input", return_value="")
@patch("cli.requests.post")
def test_add_item_rejects_empty_name(mock_post, mock_input, capsys):
    cli.add_item()

    mock_post.assert_not_called()
    assert "cannot be empty" in capsys.readouterr().out


# ---------- updating ----------

@patch("builtins.input", side_effect=["1", "4.25", "35", ""])
@patch("cli.requests.patch")
def test_update_item_sends_price_and_stock(mock_patch, mock_input):
    mock_patch.return_value = make_fake_response(200, dict(FAKE_ITEM, price=4.25, stock=35))

    cli.update_item()

    sent = mock_patch.call_args.kwargs["json"]
    assert sent == {"price": 4.25, "stock": 35}


# ---------- deleting ----------

@patch("builtins.input", side_effect=["1", "y"])
@patch("cli.requests.delete")
def test_delete_item_after_confirmation(mock_delete, mock_input):
    mock_delete.return_value = make_fake_response(200, {"message": "Item deleted", "id": 1})

    cli.delete_item()

    mock_delete.assert_called_once_with(f"{cli.BASE_URL}/inventory/1")


@patch("builtins.input", side_effect=["1", "n"])
@patch("cli.requests.delete")
def test_delete_cancelled(mock_delete, mock_input, capsys):
    cli.delete_item()

    mock_delete.assert_not_called()
    assert "cancelled" in capsys.readouterr().out


# ---------- OpenFoodFacts search ----------

@patch("builtins.input", side_effect=["b", "3017620422003"])
@patch("cli.requests.get")
def test_find_by_barcode(mock_get, mock_input, capsys):
    mock_get.return_value = make_fake_response(200, dict(FAKE_ITEM, product_name="Nutella"))

    cli.find_on_openfoodfacts()

    mock_get.assert_called_once_with(f"{cli.BASE_URL}/external/product/3017620422003")
    assert "Nutella" in capsys.readouterr().out


# ---------- error handling in the main loop ----------

@patch("builtins.input", side_effect=["1", "0"])
@patch("cli.view_all_items", side_effect=__import__("requests").ConnectionError)
def test_main_survives_connection_error(mock_view, mock_input, capsys):
    cli.main()  # must not crash even though the API is "down"

    output = capsys.readouterr().out
    assert "Cannot reach the API" in output
    assert "Goodbye" in output
