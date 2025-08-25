import pandas as pd
from sentiment_analysis import compute_sentiment, get_sentiment_series_all
from forecasting import prepare_weekly_forecast_all
from visualization import plot_all_products_subplots
from summary import generate_summary

# ------------------------
# 1) Load processed dataset
# ------------------------
df = pd.read_pickle("processed_reviews.pkl")

# ------------------------
# 2) Sentiment Analysis
# ------------------------
df = compute_sentiment(df)  # compute hybrid sentiment scores
sentiment_dict = get_sentiment_series_all(df)  # per-product weekly sentiment series

# ------------------------
# 3) Forecasting per product
# ------------------------
forecast_results = prepare_weekly_forecast_all(df, periods=12, smooth_window=3)

# ------------------------
# 4) Classification
# ------------------------
product_classification = {}
for asin, data in forecast_results.items():
    forecast_series = data['forecast']['yhat']
    # simple rule for classification
    product_classification[asin] = "Positive" if forecast_series.mean() > 0 else "Negative"

# ------------------------
# 5) Visualization for all products
# ------------------------
plot_all_products_subplots(forecast_results, sentiment_dict, product_classification)

# ------------------------
# 6) Summary report
# ------------------------
summary_df = generate_summary(
    products=forecast_results.keys(),
    forecast_results={k: v['forecast']['yhat'] for k, v in forecast_results.items()},
    classification_dict=product_classification,
    sentiment_dict=sentiment_dict
)

print("\n📊 Product Future Sentiment Summary:\n", summary_df.head())
