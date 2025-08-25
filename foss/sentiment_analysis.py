import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

# Download resources if not available
nltk.download('vader_lexicon', quiet=True)
sid = SentimentIntensityAnalyzer()

def vader_sent(text):
    """Compute sentiment using VADER"""
    try:
        return sid.polarity_scores(text)['compound']
    except:
        return 0

def textblob_sent(text):
    """Compute sentiment using TextBlob"""
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return 0

def apply_sentiment(df):
    """Apply VADER + TextBlob sentiment analysis on dataframe"""
    df['vader_score'] = df['en_text'].map(vader_sent)
    df['tb_score'] = df['en_text'].map(textblob_sent)
    df['vader_label'] = df['vader_score'].apply(
        lambda s: 'Positive' if s > 0.05 else ('Negative' if s < -0.05 else 'Neutral')
    )
    return df

