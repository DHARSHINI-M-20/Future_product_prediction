// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ProductDashboard from "./ProductDashboard";
import GraphPage from "./GraphPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ProductDashboard />} />
        <Route path="/graph/:productName" element={<GraphPage />} />
      </Routes>
    </Router>
  );
}

export default App;
