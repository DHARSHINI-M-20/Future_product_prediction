import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_sentiment(data, periods=12):
    """Forecast sentiment trend using Exponential Smoothing"""
    if len(data) < 6:
        return pd.Series([], dtype=float)
    try:
        model = ExponentialSmoothing(data, trend='add', seasonal=None).fit()
        return model.forecast(periods)
    except:
        return pd.Series([], dtype=float)

def classify_future_sentiment(forecast):
    """Classify forecast sentiment trend"""
    if forecast.empty:
        return "Insufficient data"
    avg_forecast = forecast.mean()
    if avg_forecast > 0.1:
        return "Likely to improve"
    elif avg_forecast < -0.1:
        return "Likely to decline"
    else:
        return "Stable"

