import pandas as pd
import json

# Load your pickle
df = pd.read_pickle("processed_reviews.pkl")

# Keep only useful columns
clean = df[["asin", "reviewTime", "overall", "fnet_embedding"]].dropna()

# Convert numpy arrays to JSON strings
clean["fnet_embedding"] = clean["fnet_embedding"].apply(lambda x: json.dumps(x.tolist()))

# Save as CSV
clean.to_csv("clean_reviews.csv", index=False)

print("✅ clean_reviews.csv created with", len(clean), "rows (embeddings in JSON format)")
