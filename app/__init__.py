from datetime import datetime as DateTime
from multiprocessing import Process

from typing import Optional

from app.analysis import analysis
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker

def start_app(symbol: str, config_spread_sheet_id: str, alpha_vantage_id: str) -> None:
    def _ticker_callback(now: DateTime, interval: float) -> None:
        Process(name=str(now), target=analysis, args=(now, symbol, interval, alpha_vantage_id)).start()

    ticker: Ticker = Ticker(config_spread_sheet_id, _ticker_callback)
    ticker.run() 
