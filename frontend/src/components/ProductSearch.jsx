import { useState } from "react";
import { searchExternal } from "../api";

// Search the real OpenFoodFacts API by product name and
// let the user add a result straight into the inventory.
export default function ProductSearch({ onAddProduct }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    try {
      const products = await searchExternal(query.trim());
      setResults(products);
      if (products.length === 0) {
        setError("No products found for that name.");
      }
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSearch}>
        <div className="form-row">
          <input
            placeholder="Search OpenFoodFacts by name…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      {results.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Brand</th>
              <th>Barcode</th>
              <th>Nutriscore</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {results.map((product, index) => (
              <tr key={index}>
                <td>{product.product_name || "-"}</td>
                <td>{product.brands || "-"}</td>
                <td>{product.barcode || "-"}</td>
                <td>{product.nutriscore_grade ? product.nutriscore_grade.toUpperCase() : "-"}</td>
                <td>
                  <button onClick={() => onAddProduct(product)}>Add to inventory</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
