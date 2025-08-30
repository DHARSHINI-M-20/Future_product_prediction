import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import "./App.css";
import ProductDashboard from "./ProductDashboard";
import GraphPage from "./GraphPage";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🔮 Future Product Prediction</h1>
        <h2>Analyze Amazon Products</h2>

        {/* Navigation */}
        <nav style={{ marginBottom: 20 }}>
          <Link to="/" style={{ marginRight: 15, color: "white", textDecoration: "none" }}>
            🏠 Dashboard
          </Link>
        </nav>

        <Routes>
          <Route path="/" element={<ProductDashboard />} />
          <Route path="/graph/:productName" element={<GraphPage />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;
