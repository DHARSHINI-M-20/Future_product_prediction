import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd

nltk.download('vader_lexicon', quiet=True)
sid = SentimentIntensityAnalyzer()

def vader_sent(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0
    try:
        return sid.polarity_scores(text)["compound"]
    except:
        return 0.0

def textblob_sent(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return 0.0

def label_sentiment(score: float) -> str:
    if score >= 0.6:
        return "Strong Positive"
    elif score > 0.05:
        return "Mild Positive"
    elif score <= -0.6:
        return "Strong Negative"
    elif score < -0.05:
        return "Mild Negative"
    else:
        return "Neutral"

def compute_sentiment(df: pd.DataFrame, text_column="en_text") -> pd.DataFrame:
    df = df.copy()
    df["vader_score"] = df[text_column].map(vader_sent)
    df["tb_score"] = df[text_column].map(textblob_sent)
    df["hybrid_score"] = df[["vader_score", "tb_score"]].mean(axis=1)
    df["sentiment_label"] = df["hybrid_score"].apply(label_sentiment)
    df["confidence"] = df["hybrid_score"].apply(lambda s: round(abs(s), 3))
    return df

def get_sentiment_series_all(df: pd.DataFrame, date_column="reviewTime", text_column="en_text", freq='W') -> dict:
    """
    Returns sentiment series for all products.
    
    Output: {asin: pd.Series indexed by date, values = avg hybrid_score}
    """
    df_sent = compute_sentiment(df, text_column)
    df_sent[date_column] = pd.to_datetime(df_sent[date_column], errors='coerce')
    df_sent = df_sent.dropna(subset=[date_column])

    sentiment_series_dict = {}
    for asin, group in df_sent.groupby("asin"):
        series = group.set_index(date_column)["hybrid_score"].resample(freq).mean()
        sentiment_series_dict[asin] = series

    return sentiment_series_dict
