from typing import Dict, Optional, Any, List

from app.ticker import Ticker
from app.google.google_sheet import GoogleSheet
from app.constants import CONFIG_PLACEMENT, TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTERVAL


def get_trading_config(google_sheet: GoogleSheet) -> Optional[Dict[str, Any]]:
    values: Optional[List[List[Any]]] = google_sheet.read(
        CONFIG_PLACEMENT,
        major_dimension='COLUMNS'
    )

    if values and len(values[0]) == 4:
        config: List[Any] = values[0]
        return {
            TIMEZONE: config[0],
            OPENING_HOURS: config[1],
            CLOSING_HOURS: config[2],
            INTERVAL: config[3],
        }

    return None

def trader(trade_sheet: GoogleSheet, historical_sheet: GoogleSheet) -> None:
    print('trader')

def start_app(trade_spread_sheet_id: str, historical_spread_sheet_id: str) -> None:
    trade_sheet: GoogleSheet = GoogleSheet(trade_spread_sheet_id)
    historical_sheet: GoogleSheet = GoogleSheet(historical_spread_sheet_id)

    config: Optional[Dict[str, Any]] = get_trading_config(trade_sheet)

    if config:

        def ticker_callback() -> None:
            trader(trade_sheet, historical_sheet)

        ticker: Ticker = Ticker(ticker_callback, **config)
        ticker.run()
