import pandas as pd
from sentiment_analysis import apply_sentiment
from forecasting import forecast_sentiment, classify_future_sentiment
from visualization import plot_sentiment
from summary import generate_summary

# 1) Load processed dataset
df = pd.read_pickle("processed_reviews.pkl")

# 2) Sentiment Analysis
df = apply_sentiment(df)

# 3) Date conversion
df['date'] = pd.to_datetime(df['reviewTime'], errors='coerce')
analysis_df = df[['date', 'overall', 'verified', 'reviewerID', 'asin',
                  'reviewerName', 'en_text', 'vader_score', 'tb_score',
                  'vader_label', 'fnet_embedding']].dropna(subset=['date'])

# 4) Weekly aggregation
weekly_product = (
    analysis_df.set_index('date')
    .groupby('asin')
    .resample('W-SUN')
    .agg({
        'vader_score': 'mean',
        'tb_score': 'mean',
        'overall': 'mean',
        'reviewerID': 'count'
    })
    .rename(columns={'reviewerID': 'review_count'})
    .reset_index()
)

# 5) Forecasting per product
forecast_results = {}
products = weekly_product['asin'].unique()

for product in products:
    product_data = weekly_product[weekly_product['asin'] == product].set_index('date').sort_index()
    product_data.index = product_data.index.to_period('W')
    sentiment_series = product_data['vader_score'].fillna(0)

    forecast = forecast_sentiment(sentiment_series)
    forecast_results[product] = forecast

# 6) Classification
product_classification = {p: classify_future_sentiment(forecast_results[p]) for p in products}

# 7) Visualization for top 3 products
top_products = weekly_product.groupby('asin')['review_count'].sum().sort_values(ascending=False).head(3).index

for product in top_products:
    product_data = weekly_product[weekly_product['asin'] == product].set_index('date').sort_index()
    sentiment_series = product_data['vader_score'].fillna(0)
    forecast = forecast_results[product]
    classification = product_classification[product]

    plot_sentiment(product, product_data, sentiment_series, forecast, classification)

# 8) Summary report
summary_df = generate_summary(products, forecast_results, product_classification)
print("\n📊 Product Future Sentiment Summary:\n", summary_df.head())

