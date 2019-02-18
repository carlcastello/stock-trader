from time import sleep
from datetime import datetime as Datetime

from app.google.google_sheet import GoogleSheet
from app.api.alpha_vantage.stock_time_series import StockTimeSeries

def analysis(now: Datetime, symbol: str, interval: int, alpha_vantage_id: str,) -> None:
    print(now, symbol, interval, alpha_vantage_id)


if __name__ == "__main__":
    pass