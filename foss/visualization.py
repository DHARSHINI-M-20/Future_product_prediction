import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

def plot_product_forecast_subplots(asin, data_dict, sentiment_series=None, classification=""):
    """
    Plot weekly review forecast and sentiment in two subplots for a single product.
    
    Args:
        asin: product ASIN
        data_dict: forecast_data_dict returned from forecaste.py
        sentiment_series: optional pd.Series or numpy array
        classification: optional string for title
    """
    entry = data_dict.get(asin)
    if entry is None:
        print(f"No forecast data for ASIN: {asin}")
        return

    name = entry['name']
    df_prophet = entry['df_prophet']
    forecast = entry['forecast']
    smoothed = entry['smoothed']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # ----------------- Top subplot: Review counts -----------------
    ax1.plot(df_prophet['ds'].to_numpy(), df_prophet['y'].to_numpy(), label="Actual Reviews", color="blue")
    ax1.plot(df_prophet['ds'].to_numpy(), smoothed.to_numpy(), 'c--', label="Smoothed Reviews")
    ax1.plot(forecast['ds'].to_numpy(), forecast['yhat'].to_numpy(), color="orange", label="Model Fit")

    forecast_start = df_prophet['ds'].max()
    future_forecast = forecast[forecast['ds'] > forecast_start]
    ax1.plot(future_forecast['ds'].to_numpy(), future_forecast['yhat'].to_numpy(), color="red", label="Future Prediction")
    ax1.axvline(x=forecast_start, color="gray", linestyle="--", label="Forecast Start")

    ax1.set_ylabel("Review Count")
    ax1.set_title(f"{name} - Weekly Review Forecast\nClassification: {classification}", fontsize=14)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # ----------------- Bottom subplot: Sentiment -----------------
    if sentiment_series is not None:
        # If pandas Series
        if isinstance(sentiment_series, pd.Series):
            if isinstance(sentiment_series.index, pd.PeriodIndex):
                x_index = sentiment_series.index.to_timestamp().to_numpy()
            elif isinstance(sentiment_series.index, pd.DatetimeIndex):
                x_index = sentiment_series.index.to_numpy()
            else:
                x_index = np.array(sentiment_series.index)
            y_values = sentiment_series.to_numpy()
        else:  # Already numpy array
            x_index = np.arange(len(sentiment_series))
            y_values = sentiment_series

        ax2.plot(x_index, y_values, label="Hybrid Sentiment", color='green', linestyle='--')
        ax2.set_ylabel("Hybrid Sentiment Score")
        ax2.set_xlabel("Date")
        ax2.legend()
        ax2.grid(alpha=0.3)

    # ----------------- Format x-axis -----------------
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax2.get_xticklabels(), rotation=45)

    plt.tight_layout()
    plt.show()


def plot_all_products_subplots(data_dict, sentiment_dict=None, classification_dict=None):
    """
    Plot all products separately with two subplots each.
    
    Args:
        data_dict: forecast_data_dict
        sentiment_dict: optional {asin: sentiment_series or numpy array}
        classification_dict: optional {asin: string}
    """
    for asin in data_dict.keys():
        sentiment = sentiment_dict.get(asin) if sentiment_dict else None
        classification = classification_dict.get(asin, "") if classification_dict else ""
        plot_product_forecast_subplots(asin, data_dict, sentiment, classification)
