import matplotlib.pyplot as plt
import pandas as pd

def plot_sentiment(product, product_data, sentiment_series, forecast, classification):
    """Plot historical + forecasted sentiment"""

    # Ensure index is datetime
    if isinstance(sentiment_series.index, pd.PeriodIndex):
        x_index = sentiment_series.index.to_timestamp().to_numpy()
    else:  # already datetime
        x_index = sentiment_series.index.to_numpy()

    plt.figure(figsize=(12,6))
    plt.plot(x_index, sentiment_series.values, label='Avg Sentiment (VADER)')

    if not forecast.empty:
        if isinstance(forecast.index, pd.PeriodIndex):
            x_forecast = forecast.index.to_timestamp().to_numpy()
        else:
            x_forecast = forecast.index.to_numpy()

        plt.plot(x_forecast, forecast.values, label='Forecast Sentiment', linestyle='--')

    plt.title(f'Sentiment Trend and Forecast for Product {product}\nClassification: {classification}')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score (VADER)')
    plt.legend()
    plt.show()

