import pandas as pd
import re
from transformers import FNetModel, FNetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import torch
import numpy as np
from langdetect import detect
from googletrans import Translator

# 1) Load CSV
df = pd.read_csv("amazon_reviews.csv")
print("Columns in file:", df.columns)

# 2) Clean text (reviewText + summary)
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

df['cleaned_text'] = (df['reviewText'].fillna("") + " " + df['summary'].fillna("")).map(clean_text)

# 2 Detect language and translate Tamil to English
translator = Translator()

def detect_and_translate(text):
    try:
        if not text.strip():
            return ""
        lang = detect(text)
        if lang == 'ta':
            return translator.translate(text, src='ta', dest='en').text
        else:
            return text
    except:
        return text

df['en_text'] = df['cleaned_text'].map(detect_and_translate)

# 3) Sentiment Analysis
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

# 4) FNet embedding
tokenizer = FNetTokenizer.from_pretrained("google/fnet-base")
model = FNetModel.from_pretrained("google/fnet-base")

def fnet_embedding(text):
    if not isinstance(text, str) or text.strip() == "":
        return torch.zeros(model.config.hidden_size)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embedding

df['fnet_embedding'] = df['en_text'].apply(lambda x: fnet_embedding(x).numpy())

# 5) Convert reviewTime to datetime
df['date'] = pd.to_datetime(df['reviewTime'], errors='coerce')


analysis_df = df[['date', 'overall', 'verified', 'reviewerID', 'asin',
                  'reviewerName', 'en_text', 'vader_score', 'tb_score', 'vader_label', 'fnet_embedding']].dropna(subset=['date'])

# 7) Aggregate weekly sentiment and ratings per product
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

# 8) Forecasting future sentiment
def forecast_sentiment(data, periods=12):
    if len(data) < 6:
        return pd.Series([], dtype=float)
    try:
        model = ExponentialSmoothing(data, trend='add', seasonal=None).fit()
        forecast = model.forecast(periods)
        return forecast
    except:
        return pd.Series([], dtype=float)

forecast_results = {}
products = weekly_product['asin'].unique()

for product in products:
    product_data = weekly_product[weekly_product['asin'] == product].set_index('date').sort_index()
    product_data.index = product_data.index.to_period('W')
    sentiment_series = product_data['vader_score'].fillna(0)
    forecast = forecast_sentiment(sentiment_series)
    forecast_results[product] = forecast

# 9) Classify future sentiments
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

# 10) Plot sentiment and forecast
top_products = weekly_product.groupby('asin')['review_count'].sum().sort_values(ascending=False).head(3).index

for product in top_products:
    product_data = weekly_product[weekly_product['asin'] == product].set_index('date').sort_index()
    sentiment_series = product_data['vader_score'].fillna(0)
    forecast = forecast_results[product]

    plt.figure(figsize=(12,6))
    x_index = sentiment_series.index.to_numpy()
    plt.plot(x_index, sentiment_series.values, label='Avg Sentiment (VADER)')

    if not forecast.empty:
        x_forecast = forecast.index.to_numpy()
        plt.plot(x_forecast, forecast.values, label='Forecast Sentiment', linestyle='--')

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
