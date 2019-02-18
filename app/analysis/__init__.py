from time import sleep
from pandas import DataFrame
from datetime import datetime as Datetime

from typing import Optional

from app.google.google_sheet import GoogleSheet

def analysis(now: Datetime, symbol: str, interval: float, time_stock_series_df: DataFrame) -> None:
    print(time_stock_series_df)

if __name__ == "__main__":
    pass