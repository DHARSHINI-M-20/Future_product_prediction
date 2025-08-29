import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const PRODUCT_OPTIONS = [
  "phone case", "shirt", "socks", "chain armament", "hat", "cap", "red hat", "kit"
];

function ProductDashboard() {
  const [selectedProduct, setSelectedProduct] = useState("");
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleProductSelect = async (product) => {
    setSelectedProduct(product);
    setSummary(null);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:5000/product_summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_name: product }),
      });
      if (!res.ok) throw new Error("Summary not found");
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      setError("Could not fetch summary");
    }
  };

  const handleShowTrend = () => {
    if (selectedProduct) {
      navigate(`/graph/${encodeURIComponent(selectedProduct)}`);
    }
  };

  return (
    <div>
      <h1>Product Dashboard</h1>

      {/* Product Selector */}
      <div>
        {PRODUCT_OPTIONS.map((product) => (
          <div key={product}>
            <input
              type="radio"
              id={product}
              checked={selectedProduct === product}
              onChange={() => handleProductSelect(product)}
            />
            <label htmlFor={product}>{product}</label>
          </div>
        ))}
      </div>

      {/* Show Summary */}
      {summary && (
        <div style={{ marginTop: 20, padding: 10, border: "1px solid #ccc", borderRadius: 8 }}>
          <h2>📊 {summary.product_name} Summary</h2>
          <p><strong>ASIN:</strong> {summary.asin}</p>
          <p><strong>Historical:</strong> {JSON.stringify(summary.historical_summary)}</p>
          <p><strong>Forecast:</strong> {JSON.stringify(summary.forecast_summary)}</p>
        </div>
      )}

      {/* Trend Button */}
      <button onClick={handleShowTrend} disabled={!selectedProduct} style={{ marginTop: 10 }}>
        Show Trend
      </button>

      {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
    </div>
  );
}

export default ProductDashboard;
