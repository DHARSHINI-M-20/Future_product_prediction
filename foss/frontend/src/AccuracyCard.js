import React, { useEffect, useState } from "react";

function AccuracyCard() {
  const [metrics, setMetrics] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/classification_accuracy");
        if (!res.ok) throw new Error("API error");
        const data = await res.json();
        setMetrics(data.metrics);
      } catch (e) {
        setErr("❌ Failed to load classification accuracy");
      }
    };
    run();
  }, []);

  if (err) return <p style={{ color: "red" }}>{err}</p>;
  if (!metrics) return <p>Loading classification accuracy…</p>;

  return (
    <div
      style={{
        marginTop: 20,
        padding: 20,
        borderRadius: 10,
        background: "rgba(255,255,255,0.1)",
      }}
    >
      <h3>🤖 Classification Model Accuracy</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <tbody>
          <tr><td><strong>Accuracy</strong></td><td>{(metrics.accuracy * 100).toFixed(2)}%</td></tr>
          <tr><td><strong>Total Samples</strong></td><td>{metrics.summary.total_samples}</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default AccuracyCard;

