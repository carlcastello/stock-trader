from pandas import DataFrame
from datetime import datetime as DateTime
from multiprocessing import Process

from typing import Optional

from app.api.alpha_vantage.stock_time_series import StockTimeSeries
from app.analysis import analysis
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker

def start_app(symbol: str, config_spread_sheet_id: str, alpha_vantage_id: str) -> None:
    time_stock_series_df: Optional[DataFrame] = None
    
    def _ticker_callback(now: DateTime, interval: float) -> None:
        nonlocal time_stock_series_df

        stock_time_series: StockTimeSeries = StockTimeSeries(alpha_vantage_id, symbol, round(1))
        if not time_stock_series_df:
            time_stock_series_df = DataFrame(
                stock_time_series.get(),
                columns=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
            )

        Process(name=str(now), target=analysis, args=(now, symbol, interval, time_stock_series_df)).start()

    ticker: Ticker = Ticker(config_spread_sheet_id, _ticker_callback)
    ticker.run() 
