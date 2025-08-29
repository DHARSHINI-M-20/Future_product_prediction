import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os

def plot_product_forecast_subplots(asin, data_dict, sentiment_series=None, classification="", save_path=None):
    """
    Plot weekly review forecast and sentiment in two subplots for a single product.

    Args:
        asin (str): ASIN of the product
        data_dict (dict): dict containing forecast data per ASIN
        sentiment_series (pd.Series or list/np.array): optional sentiment series
        classification (str): optional classification label
        save_path (str): optional path to save the plot (PNG)
    """
    entry = data_dict.get(asin)
    if entry is None:
        print(f"No forecast data for ASIN: {asin}")
        return

    name = entry.get('name', asin)
    df_prophet = entry.get('df_prophet')
    forecast = entry.get('forecast')
    smoothed = entry.get('smoothed')

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    # -----------------------
    # Top subplot: Review Count
    # -----------------------
    if df_prophet is not None and 'y' in df_prophet:
        try:
            x_hist = pd.to_datetime(df_prophet['ds']).to_numpy()
        except Exception:
            x_hist = df_prophet['ds'].to_numpy() if 'ds' in df_prophet else np.arange(len(df_prophet))
        y_hist = df_prophet['y'].to_numpy()
        ax1.plot(x_hist, y_hist, label="Actual Reviews", marker='o', color='blue')

    if smoothed is not None:
        try:
            x_smooth = pd.to_datetime(df_prophet['ds']).to_numpy()
        except Exception:
            x_smooth = smoothed.index.to_numpy()
        ax1.plot(x_smooth, smoothed.to_numpy(), 'c--', label="Smoothed Reviews")

    if forecast is not None and 'yhat' in forecast:
        try:
            x_forecast = pd.to_datetime(forecast['ds']).to_numpy()
        except Exception:
            x_forecast = forecast['ds'].to_numpy() if 'ds' in forecast else np.arange(len(forecast))
        y_forecast = forecast['yhat'].to_numpy()
        ax1.plot(x_forecast, y_forecast, color="orange", label="Model Fit/Prediction")

        # Highlight future prediction if possible
        try:
            forecast_start = pd.to_datetime(df_prophet['ds']).max()
            future_mask = pd.to_datetime(forecast['ds']) > forecast_start
            if future_mask.any():
                future_forecast = forecast[future_mask]
                ax1.plot(pd.to_datetime(future_forecast['ds']).to_numpy(),
                         future_forecast['yhat'].to_numpy(),
                         color="red", label="Future Prediction")
                ax1.axvline(x=forecast_start, color="gray", linestyle="--", label="Forecast Start")
        except Exception:
            pass

    ax1.set_ylabel("Review Count")
    ax1.set_title(f"{name} - Weekly Review Forecast\nClassification: {classification}", fontsize=12)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # -----------------------
    # Bottom subplot: Sentiment
    # -----------------------
    if sentiment_series is not None:
        if isinstance(sentiment_series, pd.Series):
            if isinstance(sentiment_series.index, pd.PeriodIndex):
                x_index = sentiment_series.index.to_timestamp().to_numpy()
            elif isinstance(sentiment_series.index, pd.DatetimeIndex):
                x_index = sentiment_series.index.to_numpy()
            else:
                x_index = np.array(sentiment_series.index)
            y_values = sentiment_series.to_numpy()
        else:
            x_index = np.arange(len(sentiment_series))
            y_values = np.array(sentiment_series)

        ax2.plot(x_index, y_values, label="Hybrid Sentiment", linestyle='--', marker='x', color='green')

    ax2.set_ylabel("Hybrid Sentiment Score")
    ax2.set_xlabel("Date")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # -----------------------
    # Format X-axis if datetime
    # -----------------------
    try:
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.setp(ax2.get_xticklabels(), rotation=45)
    except Exception:
        pass

    plt.tight_layout()

    # -----------------------
    # Save or show
    # -----------------------
    if save_path:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()
