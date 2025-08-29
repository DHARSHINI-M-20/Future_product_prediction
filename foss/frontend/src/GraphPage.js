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
  const { productName } = useParams(); // get from URL
  const [data, setData] = useState([]);

  useEffect(() => {
    const encodedProduct = encodeURIComponent(productName);

    fetch(`http://127.0.0.1:5000/graph/${encodedProduct}`)
      .then((res) => res.json())
      .then((result) => {
        console.log("API Response:", result);

        // Convert sentiment data
        const sentimentData = (result.sentiment || []).map((item) => ({
          date: new Date(item.date).toLocaleDateString(),
          current: item.score,
        }));

        // Convert forecast data
        const forecastData = (result.forecast || []).map((item) => ({
          date: new Date(item.date).toLocaleDateString(),
          future: item.yhat,
        }));

        // Merge by date
        const merged = {};
        sentimentData.forEach((s) => {
          merged[s.date] = { ...(merged[s.date] || {}), ...s };
        });
        forecastData.forEach((f) => {
          merged[f.date] = { ...(merged[f.date] || {}), ...f };
        });

        setData(Object.keys(merged).map((d) => ({ date: d, ...merged[d] })));
      })
      .catch((err) => console.error("Error fetching data:", err));
  }, [productName]);

  return (
    <div style={{ width: "100%", height: 500 }}>
      <h2 className="text-xl font-bold text-center mb-4">
        📈 Sentiment Trend for "{productName}"
      </h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" angle={-45} textAnchor="end" height={70} />
          <YAxis />
          <Tooltip />
          <Legend />

          {/* Current sentiment = Blue */}
          <Line
            type="monotone"
            dataKey="current"
            stroke="#1f77b4"
            dot={false}
            name="Current Sentiment"
          />

          {/* Future forecast = Orange */}
          <Line
            type="monotone"
            dataKey="future"
            stroke="#ff7f0e"
            dot={false}
            name="Future Sentiment"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default GraphPage;
