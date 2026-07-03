import { useState } from "react";

// Table of all inventory items with edit / delete / enhance buttons.
export default function InventoryList({ items, onUpdate, onDelete, onEnhance }) {
  // id of the row currently being edited (null = none)
  const [editingId, setEditingId] = useState(null);
  const [editPrice, setEditPrice] = useState("");
  const [editStock, setEditStock] = useState("");

  function startEditing(item) {
    setEditingId(item.id);
    setEditPrice(item.price);
    setEditStock(item.stock);
  }

  function saveEdit(id) {
    onUpdate(id, { price: Number(editPrice), stock: Number(editStock) });
    setEditingId(null);
  }

  if (items.length === 0) {
    return <p>The inventory is empty.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Product</th>
          <th>Brand</th>
          <th>Barcode</th>
          <th>Nutriscore</th>
          <th>Price</th>
          <th>Stock</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.product_name}</td>
            <td>{item.brands || "-"}</td>
            <td>{item.barcode || "-"}</td>
            <td>{item.nutriscore_grade ? item.nutriscore_grade.toUpperCase() : "-"}</td>

            {editingId === item.id ? (
              <>
                <td>
                  <input
                    type="number"
                    step="0.01"
                    style={{ width: "70px" }}
                    value={editPrice}
                    onChange={(e) => setEditPrice(e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    style={{ width: "60px" }}
                    value={editStock}
                    onChange={(e) => setEditStock(e.target.value)}
                  />
                </td>
                <td>
                  <button onClick={() => saveEdit(item.id)}>Save</button>{" "}
                  <button className="secondary" onClick={() => setEditingId(null)}>
                    Cancel
                  </button>
                </td>
              </>
            ) : (
              <>
                <td>{Number(item.price).toFixed(2)}</td>
                <td>{item.stock}</td>
                <td>
                  <button onClick={() => startEditing(item)}>Edit</button>{" "}
                  <button className="secondary" onClick={() => onEnhance(item.id)}>
                    Enhance
                  </button>{" "}
                  <button className="danger" onClick={() => onDelete(item.id)}>
                    Delete
                  </button>
                </td>
              </>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
