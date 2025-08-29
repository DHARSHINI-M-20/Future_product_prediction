import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# summary.py

def analyze_series(series, label="Data"):
    """Return summary for a sentiment series as a dictionary (JSON safe)."""
    if len(series) == 0:
        return {"message": f"No data available for {label}"}

    series = pd.Series(series)  # ensure pandas Series
    avg_val = float(series.mean())
    last_val = float(series.iloc[-1])
    min_val, min_date = float(series.min()), str(series.idxmin())
    max_val, max_date = float(series.max()), str(series.idxmax())

    # Trend detection
    trend = "Stable"
    if len(series) > 1:
        slope = series.iloc[-1] - series.iloc[0]
        if slope > 0:
            trend = "Increasing"
        elif slope < 0:
            trend = "Decreasing"

    # Prediction based on last value
    prediction = "Likely Positive" if last_val > 0 else "Likely Negative"

    return {
        "label": label,
        "average": avg_val,
        "latest": last_val,
        "min": {"value": min_val, "date": min_date},
        "max": {"value": max_val, "date": max_date},
        "trend": trend,
        "prediction": prediction
    }


def plot_sentiment(product, sentiment_series=None, forecast_dict=None, classification=""):
    """
    Plot historical + forecasted sentiment for a product and print summaries.
    
    Args:
        product: product ASIN or name
        sentiment_series: pd.Series or numpy array
        forecast_dict: dict containing 'forecast' Series, same as visualization.py
        classification: string
    """

    plt.figure(figsize=(12, 6))

    # ---------- Historical sentiment ----------
    if sentiment_series is not None:
        if isinstance(sentiment_series, pd.Series):
            x_hist = sentiment_series.index.to_numpy() if isinstance(sentiment_series.index, pd.DatetimeIndex) else np.array(sentiment_series.index)
            y_hist = sentiment_series.to_numpy()
        else:  # numpy array
            x_hist = np.arange(len(sentiment_series))
            y_hist = sentiment_series

        plt.plot(x_hist, y_hist, label="Historical Sentiment", marker="o", color="blue")
        print(analyze_series(pd.Series(y_hist, index=x_hist), label="Historical"))

    # ---------- Forecast sentiment ----------
    if forecast_dict is not None and 'forecast' in forecast_dict:
        forecast_series = forecast_dict['forecast']['yhat']
        if isinstance(forecast_series, pd.Series):
            x_forecast = forecast_series.index.to_numpy() if isinstance(forecast_series.index, pd.DatetimeIndex) else np.array(forecast_series.index)
            y_forecast = forecast_series.to_numpy()
        else:
            x_forecast = np.arange(len(forecast_series))
            y_forecast = forecast_series

        plt.plot(x_forecast, y_forecast, label="Forecast Sentiment", linestyle="--", marker="x", color="orange")
        print(analyze_series(pd.Series(y_forecast, index=x_forecast), label="Forecast"))

    plt.title(f"Sentiment Trend for Product {product}\nClassification: {classification}")
    plt.xlabel("Date")
    plt.ylabel("Sentiment Score")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def generate_summary(products, forecast_results, classification_dict, sentiment_dict=None):
    """
    Create a summary DataFrame for all products.
    
    Args:
        products: list of ASINs
        forecast_results: dict of {asin: forecast_dict}
        classification_dict: dict of {asin: string}
        sentiment_dict: optional {asin: sentiment_series}
    """
    data = {
        "product": [],
        "classification": [],
        "forecast_mean_sentiment": [],
        "latest_sentiment": [],
    }

    for p in products:
        data["product"].append(p)
        data["classification"].append(classification_dict.get(p, ""))

        # Forecast mean sentiment
        forecast_entry = forecast_results.get(p, {})
        if 'forecast' in forecast_entry:
            forecast_mean = forecast_entry['forecast']['yhat'].mean()
        else:
            forecast_mean = np.nan
        data["forecast_mean_sentiment"].append(forecast_mean)

        # Latest sentiment
        if sentiment_dict and p in sentiment_dict:
            s = sentiment_dict[p]
            latest_val = s.iloc[-1] if isinstance(s, pd.Series) else s[-1]
        else:
            latest_val = np.nan
        data["latest_sentiment"].append(latest_val)

    return pd.DataFrame(data)


# ------------------------
# Example Run
# ------------------------
if __name__ == "__main__":
    dates_hist = pd.date_range("2025-01-01", periods=6, freq="M")
    sentiment_values = [-0.1, -0.05, 0.0, 0.2, 0.1, 0.15]
    sentiment_series = pd.Series(sentiment_values, index=dates_hist)

    dates_forecast = pd.date_range("2025-07-01", periods=3, freq="M")
    forecast_values = [0.05, 0.1, 0.25]
    forecast_series = pd.Series(forecast_values, index=dates_forecast)
    forecast_dict = {'forecast': pd.DataFrame({'yhat': forecast_series})}

    plot_sentiment(
        product="A123",
        sentiment_series=sentiment_series,
        forecast_dict=forecast_dict,
        classification="Positive"
    )

    df_summary = generate_summary(["A123"], {"A123": forecast_dict}, {"A123": "Positive"}, {"A123": sentiment_series})
    print(df_summary)
