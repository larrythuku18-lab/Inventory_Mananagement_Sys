import { useState } from "react";

const EMPTY_FORM = {
  product_name: "",
  brands: "",
  barcode: "",
  price: "",
  stock: "",
};

// Form for adding a new inventory item -> POST /inventory
export default function InventoryForm({ onAdd }) {
  const [form, setForm] = useState(EMPTY_FORM);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!form.product_name.trim()) {
      alert("Product name is required");
      return;
    }
    onAdd({
      product_name: form.product_name.trim(),
      brands: form.brands.trim(),
      barcode: form.barcode.trim(),
      price: Number(form.price) || 0,
      stock: Number(form.stock) || 0,
    });
    setForm(EMPTY_FORM); // clear the form after adding
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <input
          name="product_name"
          placeholder="Product name *"
          value={form.product_name}
          onChange={handleChange}
        />
        <input name="brands" placeholder="Brand" value={form.brands} onChange={handleChange} />
        <input name="barcode" placeholder="Barcode" value={form.barcode} onChange={handleChange} />
        <input
          name="price"
          type="number"
          step="0.01"
          placeholder="Price"
          value={form.price}
          onChange={handleChange}
        />
        <input
          name="stock"
          type="number"
          placeholder="Stock"
          value={form.stock}
          onChange={handleChange}
        />
        <button type="submit">Add item</button>
      </div>
    </form>
  );
}
