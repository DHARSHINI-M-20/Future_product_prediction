import pandas as pd
import numpy as np

def generate_summary(products, forecast_results, product_classification):
    """Generate summary dataframe"""
    summary_df = pd.DataFrame({
        'asin': products,
        'forecast_classification': [product_classification[p] for p in products],
        'forecast_mean_sentiment': [forecast_results[p].mean() if not forecast_results[p].empty else np.nan for p in products]
    })
    return summary_df

