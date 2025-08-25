import matplotlib.pyplot as plt
import pandas as pd

def analyze_series(series, label="Data"):
    """Return summary for a sentiment series"""
    avg_val = series.mean()
    last_val = series.iloc[-1]
    min_val, min_date = series.min(), series.idxmin()
    max_val, max_date = series.max(), series.idxmax()

    # Trend detection (based on slope first→last)
    if len(series) > 1:
        slope = series.iloc[-1] - series.iloc[0]
        if slope > 0:
            trend = "Increasing"
        elif slope < 0:
            trend = "Decreasing"
        else:
            trend = "Stable"
    else:
        trend = "Stable"

    # Prediction based on last value
    prediction = "Likely Positive" if last_val > 0 else "Likely Negative"

    summary = f"""
===== {label} Sentiment Summary =====
Average Sentiment: {avg_val:.2f}
Latest Sentiment: {last_val:.2f}
Minimum Sentiment: {min_val:.2f} on {min_date.date()}
Maximum Sentiment: {max_val:.2f} on {max_date.date()}
Trend: {trend}
Prediction: {prediction}
"""
    return summary


def plot_sentiment(product, product_data, sentiment_series, forecast, classification):
    """Plot historical + forecasted sentiment and print separate summaries"""

    # Ensure index is datetime
    if isinstance(sentiment_series.index, pd.PeriodIndex):
        x_index = sentiment_series.index.to_timestamp().to_numpy()
    else:
        x_index = sentiment_series.index.to_numpy()

    plt.figure(figsize=(12,6))
    plt.plot(x_index, sentiment_series.values, label='Avg Sentiment (VADER)', marker="o")

    if not forecast.empty:
        if isinstance(forecast.index, pd.PeriodIndex):
            x_forecast = forecast.index.to_timestamp().to_numpy()
        else:
            x_forecast = forecast.index.to_numpy()

        plt.plot(x_forecast, forecast.values, label='Forecast Sentiment', linestyle='--', marker="x")

    plt.title(f'Sentiment Trend and Forecast for Product {product}\nClassification: {classification}')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score (VADER)')
    plt.legend()
    plt.show()

    # ---------- PRINT SEPARATE SUMMARIES ----------
    print(analyze_series(sentiment_series, label="Historical"))
    if not forecast.empty:
        print(analyze_series(forecast, label="Forecast"))


# ------------------------
# Example Run
# ------------------------
if __name__ == "__main__":
    # Historical data
    dates_hist = pd.date_range("2025-01-01", periods=6, freq="M")
    sentiment_values = [-0.1, -0.05, 0.0, 0.2, 0.1, 0.15]
    sentiment_series = pd.Series(sentiment_values, index=dates_hist)

    # Forecast data
    dates_forecast = pd.date_range("2025-07-01", periods=3, freq="M")
    forecast_values = [0.05, 0.1, 0.25]
    forecast_series = pd.Series(forecast_values, index=dates_forecast)

    plot_sentiment(
        product="A123",
        product_data=None,
        sentiment_series=sentiment_series,
        forecast=forecast_series,
        classification="Positive"
    )
