import pandas as pd
import re
from transformers import pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np

# 1) Load CSV
df = pd.read_csv("amazon_reviews.csv")
print("Columns in file:", df.columns)

# 2) Clean text (reviewText + summary for richer context)
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

df['cleaned_text'] = (df['reviewText'].fillna("") + " " + df['summary'].fillna("")).map(clean_text)

# 3) (Optional) Translation
# Assuming reviews mostly English:
df['en_text'] = df['cleaned_text']

# 4) Sentiment Analysis
nltk.download('vader_lexicon', quiet=True)
sid = SentimentIntensityAnalyzer()

def vader_sent(text):
    try:
        return sid.polarity_scores(text)['compound']
    except:
        return 0

def textblob_sent(text):
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return 0

df['vader_score'] = df['en_text'].map(vader_sent)
df['tb_score'] = df['en_text'].map(textblob_sent)

df['vader_label'] = df['vader_score'].apply(
    lambda s: 'Positive' if s > 0.05 else ('Negative' if s < -0.05 else 'Neutral')
)

# 5) Convert reviewTime to datetime
df['date'] = pd.to_datetime(df['reviewTime'], errors='coerce')

# 6) Keep columns relevant for analysis
analysis_df = df[['date', 'overall', 'verified', 'reviewerID', 'asin',
                  'reviewerName', 'en_text', 'vader_score', 'tb_score', 'vader_label']].dropna(subset=['date'])

# 7) Aggregate weekly sentiment and ratings per product (asin)
weekly_product = (
    analysis_df.set_index('date')
    .groupby('asin')
    .resample('W-SUN')   # explicitly set weekly ending on Sunday
    .agg({
        'vader_score': 'mean',
        'tb_score': 'mean',
        'overall': 'mean',
        'reviewerID': 'count'
    })
    .rename(columns={'reviewerID': 'review_count'})
    .reset_index()
)

# 8) Forecasting future sentiment per product

def forecast_sentiment(data, periods=12):
    # data: time series pd.Series of weekly sentiment scores per product
    if len(data) < 6:
        return pd.Series([], dtype=float)
    try:
        model = ExponentialSmoothing(data, trend='add', seasonal=None).fit()
        forecast = model.forecast(periods)
        return forecast
    except:
        return pd.Series([], dtype=float)

# Store forecasts in a dictionary keyed by product asin
forecast_results = {}

products = weekly_product['asin'].unique()

for product in products:
    product_data = (
        weekly_product[weekly_product['asin'] == product]
        .set_index('date')
        .sort_index()
    )
    product_data.index = product_data.index.to_period('W')  # attach weekly frequency
    
    sentiment_series = product_data['vader_score'].fillna(0)
    forecast = forecast_sentiment(sentiment_series)
    forecast_results[product] = forecast

# 9) Classify future sentiments per product (example threshold-based)
def classify_future_sentiment(forecast):
    if forecast.empty:
        return "Insufficient data"
    avg_forecast = forecast.mean()
    if avg_forecast > 0.1:
        return "Likely to improve"
    elif avg_forecast < -0.1:
        return "Likely to decline"
    else:
        return "Stable"

product_classification = {p: classify_future_sentiment(forecast_results[p]) for p in products}

# 10) Examples - Plot sentiment and forecast for top 3 products by review count
top_products = weekly_product.groupby('asin')['review_count'].sum().sort_values(ascending=False).head(3).index

for product in top_products:
    product_data = weekly_product[weekly_product['asin'] == product].set_index('date').sort_index()
    sentiment_series = product_data['vader_score'].fillna(0)
    forecast = forecast_results[product]

    plt.figure(figsize=(12,6))
    plt.plot(sentiment_series.index, sentiment_series.values, label='Avg Sentiment (VADER)')
    if not forecast.empty:
        plt.plot(forecast.index, forecast.values, label='Forecast Sentiment', linestyle='--')
    plt.title(f'Sentiment Trend and Forecast for Product {product}\nClassification: {product_classification[product]}')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score (VADER)')
    plt.legend()
    plt.show()

# 11) Summary report
summary_df = pd.DataFrame({
    'asin': products,
    'forecast_classification': [product_classification[p] for p in products],
    'forecast_mean_sentiment': [forecast_results[p].mean() if not forecast_results[p].empty else np.nan for p in products]
})

print("Product Future Sentiment Summary:\n", summary_df.head())
