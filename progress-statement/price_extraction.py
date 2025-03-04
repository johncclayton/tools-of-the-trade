from datetime import datetime
import pandas as pd
import norgatedata


def get_closing_price_from_norgate(symbol: str, currency: str) -> float:
    """Fetches the closing price from Norgate for a given symbol and currency."""
    prior_business_day: datetime = datetime.today() - pd.offsets.BDay(1)
    try:
        price_recarray = norgatedata.price_timeseries(
            (symbol + ".au") if currency == "AUD" else symbol,
            start_date=prior_business_day,
            end_date=prior_business_day
        )
        price_dataframe = pd.DataFrame(price_recarray)
        return price_dataframe.iloc[0]['Close']
    except Exception as e:
        print(f"Error fetching price from Norgate for {symbol}: {e}")
        return 0.0  # Return a default value in case of an error

