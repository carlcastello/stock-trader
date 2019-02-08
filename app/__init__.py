from datetime import datetime as DateTime

from typing import Optional

from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker
from app.constants import CONFIG_PLACEMENT, TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTERVAL

TRADE_SHEET: Optional[GoogleSheet] = None
HISTORICAL_SHEET: Optional[GoogleSheet] = None

def _initialize_sheet(trade_spread_sheet_id: str,
                      historical_spread_sheet_id: str) -> None:

    global CONFIG_SHEET, TRADE_SHEET, HISTORICAL_SHEET

    TRADE_SHEET = GoogleSheet(trade_spread_sheet_id)
    HISTORICAL_SHEET = GoogleSheet(historical_spread_sheet_id)

def _ticker_callback(now: DateTime) -> None:
    print(now)

def start_app(config_spread_sheet_id: str,
              trade_spread_sheet_id: str,
              historical_spread_sheet_id: str) -> None:

    _initialize_sheet(trade_spread_sheet_id, historical_spread_sheet_id)

    if TRADE_SHEET and HISTORICAL_SHEET:
        ticker: Ticker = Ticker(GoogleSheet(config_spread_sheet_id), _ticker_callback)
        ticker.run()
