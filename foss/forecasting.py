import pandas as pd
from prophet import Prophet

def prepare_weekly_forecast_all(processed_reviews, periods=12, smooth_window=3):
    """
    Prepare forecast data for all products.
    
    Args:
        processed_reviews: pd.DataFrame with 'asin', 'reviewTime', 'summary'
        periods: weeks to forecast
        smooth_window: window for moving average

    Returns:
        forecast_data_dict: {asin: {'name', 'df_prophet', 'forecast', 'smoothed'}}
    """
    processed_reviews['reviewTime'] = pd.to_datetime(processed_reviews['reviewTime'], errors='coerce')
    processed_reviews = processed_reviews.dropna(subset=['reviewTime'])

    # Map asin -> human-readable name
    asin_to_name = (
        processed_reviews.groupby("asin")["summary"]
        .agg(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
        .to_dict()
    )

    # Weekly counts
    processed_reviews['year_week'] = processed_reviews['reviewTime'].dt.to_period('W').dt.start_time
    weekly_counts = processed_reviews.groupby(['asin', 'year_week']).size().reset_index(name='count')

    forecast_data_dict = {}
    for asin, name in asin_to_name.items():
        product_data = weekly_counts[weekly_counts['asin'] == asin][['year_week', 'count']]
        df_prophet = product_data.rename(columns={'year_week': 'ds', 'count': 'y'})

        if len(df_prophet) < 6:
            continue

        model = Prophet(weekly_seasonality=True, daily_seasonality=False)
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=periods, freq='W')
        forecast = model.predict(future)
        smoothed = df_prophet['y'].rolling(window=smooth_window, center=True).mean()

        forecast_data_dict[asin] = {
            'name': name,
            'df_prophet': df_prophet,
            'forecast': forecast,
            'smoothed': smoothed
        }

    return forecast_data_dict
