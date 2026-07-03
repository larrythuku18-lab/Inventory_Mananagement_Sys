import { useEffect, useState } from "react";
import InventoryList from "./components/InventoryList.jsx";
import InventoryForm from "./components/InventoryForm.jsx";
import ProductSearch from "./components/ProductSearch.jsx";
import { getAllItems, addItem, updateItem, deleteItem, enhanceItem } from "./api";

export default function App() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Load the inventory when the page first opens.
  useEffect(() => {
    loadItems();
  }, []);

  async function loadItems() {
    try {
      setItems(await getAllItems());
      setError("");
    } catch (err) {
      setError("Could not load inventory. Is the Flask server running?");
    }
  }

  function showMessage(text) {
    setMessage(text);
    setTimeout(() => setMessage(""), 3000); // hide after 3 seconds
  }

  async function handleAdd(newItem) {
    try {
      const created = await addItem(newItem);
      setItems([...items, created]);
      showMessage(`Added "${created.product_name}"`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUpdate(id, changes) {
    try {
      const updated = await updateItem(id, changes);
      setItems(items.map((item) => (item.id === id ? updated : item)));
      showMessage(`Updated "${updated.product_name}"`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this item?")) return;
    try {
      await deleteItem(id);
      setItems(items.filter((item) => item.id !== id));
      showMessage("Item deleted");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleEnhance(id) {
    try {
      const enhanced = await enhanceItem(id);
      setItems(items.map((item) => (item.id === id ? enhanced : item)));
      showMessage(`Enhanced "${enhanced.product_name}" with OpenFoodFacts data`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <header>
        <h1>Inventory Manager — Admin Portal</h1>
      </header>

      <div className="container">
        {error && <p className="error">{error}</p>}
        {message && <p className="message">{message}</p>}

        <div className="card">
          <h2>Add a new item</h2>
          <InventoryForm onAdd={handleAdd} />
        </div>

        <div className="card">
          <h2>Inventory ({items.length} items)</h2>
          <InventoryList
            items={items}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onEnhance={handleEnhance}
          />
        </div>

        <div className="card">
          <h2>Find products on OpenFoodFacts</h2>
          <ProductSearch onAddProduct={handleAdd} />
        </div>
      </div>
    </div>
  );
}
