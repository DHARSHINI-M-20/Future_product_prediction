import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const PRODUCT_OPTIONS = [
  "phone case", "shirt", "socks", "chain armament", "hat", "cap", "red hat", "kit"
];

function ProductDashboard() {
  const [selectedProduct, setSelectedProduct] = useState("");
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleProductSelect = async (product) => {
    setSelectedProduct(product);
    setSummary(null);
    setError("");
    setLoading(true);

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
      setError("❌ Could not fetch summary");
    } finally {
      setLoading(false);
    }
  };

  const handleShowTrend = () => {
    if (selectedProduct) {
      navigate(`/graph/${encodeURIComponent(selectedProduct)}`);
    }
  };

  return (
    <div>
      <h2>📌 Choose a Product</h2>

      {/* Product Buttons */}
      <div className="product-buttons">
        {PRODUCT_OPTIONS.map((product) => (
          <button
            key={product}
            className="product-btn"
            onClick={() => handleProductSelect(product)}
          >
            {product}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && <p>Loading summary…</p>}

      {/* Show Summary */}
      {summary && (
  <div
    style={{
      marginTop: 20,
      padding: 20,
      borderRadius: 10,
      background: "rgba(255,255,255,0.1)",
    }}
  >
    <h2>📊 {selectedProduct} Summary</h2>
    <p><strong>ASIN:</strong> {summary.asin}</p>

    {/* Historical Table */}
    <h3>📜 Historical</h3>
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        marginBottom: "20px",
      }}
    >
      <tbody>
        <tr><td><strong>Average</strong></td><td>{summary.historical_summary.average}</td></tr>
        <tr><td><strong>Latest</strong></td><td>{summary.historical_summary.latest}</td></tr>
        <tr><td><strong>Max</strong></td><td>{JSON.stringify(summary.historical_summary.max)}</td></tr>
        <tr><td><strong>Min</strong></td><td>{JSON.stringify(summary.historical_summary.min)}</td></tr>
        <tr><td><strong>Prediction</strong></td><td>{summary.historical_summary.prediction}</td></tr>
        <tr><td><strong>Trend</strong></td><td>{summary.historical_summary.trend}</td></tr>
      </tbody>
    </table>

    {/* Forecast Table */}
    <h3>🔮 Forecast</h3>
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
      }}
    >
      <tbody>
        <tr><td><strong>Average</strong></td><td>{summary.forecast_summary.average}</td></tr>
        <tr><td><strong>Latest</strong></td><td>{summary.forecast_summary.latest}</td></tr>
        <tr><td><strong>Max</strong></td><td>{JSON.stringify(summary.forecast_summary.max)}</td></tr>
        <tr><td><strong>Min</strong></td><td>{JSON.stringify(summary.forecast_summary.min)}</td></tr>
        <tr><td><strong>Prediction</strong></td><td>{summary.forecast_summary.prediction}</td></tr>
        <tr><td><strong>Trend</strong></td><td>{summary.forecast_summary.trend}</td></tr>
      </tbody>
    </table>
  </div>
)}


      {/* Show Trend Button */}
      <div className="actions">
        <button
          onClick={handleShowTrend}
          className="action-btn"
          disabled={!selectedProduct}
        >
          📈 Show Trend
        </button>
      </div>

      {/* Error */}
      {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
    </div>
  );
}

export default ProductDashboard;
