import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useParams } from "react-router-dom";

function GraphPage() {
  const { productName } = useParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setErr("");
      try {
        const encodedProduct = encodeURIComponent(productName);
        const res = await fetch(`http://127.0.0.1:5000/graph/${encodedProduct}`);
        if (!res.ok) throw new Error(`Graph API error (${res.status})`);
        const result = await res.json();

        const sentimentData = (result.sentiment || []).map((item) => ({
          date: new Date(item.date).toLocaleDateString(),
          current: item.score,
        }));

        const forecastData = (result.forecast || []).map((item) => ({
          date: new Date(item.date).toLocaleDateString(),
          future: item.yhat,
        }));

        const merged = {};
        sentimentData.forEach((s) => {
          merged[s.date] = { ...(merged[s.date] || {}), ...s };
        });
        forecastData.forEach((f) => {
          merged[f.date] = { ...(merged[f.date] || {}), ...f };
        });

        const rows = Object.keys(merged)
          .sort((a, b) => new Date(a) - new Date(b))
          .map((d) => ({ date: d, ...merged[d] }));

        setData(rows);
      } catch (e) {
        console.error(e);
        setErr("Failed to load graph data.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [productName]);

  return (
    <div
      className="graph-container container"
      style={{
        background: "#1e1e2f",   // Dark background
        padding: "20px",
        borderRadius: "12px",
        color: "white",
      }}
    >
      <h2 className="page-title">📈 Sentiment Trend for “{productName}”</h2>

      {loading && <p>Loading chart…</p>}
      {err && <p className="error">{err}</p>}

      {!loading && !err && (
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={70} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="current" stroke="#42fa09ff" dot={false} name="Current Sentiment" />
            <Line type="monotone" dataKey="future" stroke="#ff7f0e" dot={false} name="Future Prediction" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default GraphPage;
