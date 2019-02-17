from datetime import datetime as DateTime

from typing import Optional

from app.alpha_vantage.stock_time_series import StockTimeSeries
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker
# from app.constants import CONFIG_PLACEMENT, TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTERVAL

TRADE_SHEET: Optional[GoogleSheet] = None
HISTORICAL_SHEET: Optional[GoogleSheet] = None
CONFIG_SHEET: Optional[GoogleSheet] = None

def _initialize_sheet(config_spread_sheet_id: str,
                      trade_spread_sheet_id: str,
                      historical_spread_sheet_id: str) -> None:

    global CONFIG_SHEET, TRADE_SHEET, HISTORICAL_SHEET

    TRADE_SHEET = GoogleSheet(trade_spread_sheet_id)
    HISTORICAL_SHEET = GoogleSheet(historical_spread_sheet_id)
    CONFIG_SHEET = GoogleSheet(config_spread_sheet_id)


def _ticker_callback(now: DateTime, new_day: bool=True) -> None:
    global TRADE_SHEET, HISTORICAL_SHEET
    print('------------------------------------')
    print(now)
    
    # date_string: str = now.strftime('%Y-%m-%d')
    # if new_day and TRADE_SHEET and HISTORICAL_SHEET:
        
    #     HISTORICAL_SHEET.create_sheet(date_string)
    #     TRADE_SHEET.create_sheet(date_string)
    # print('Callback  : ', DateTime.now())

        

def start_app(config_spread_sheet_id: str,
              trade_spread_sheet_id: str,
              historical_spread_sheet_id: str,
              alpha_vantage_id: str) -> None:

    _initialize_sheet(config_spread_sheet_id, trade_spread_sheet_id, historical_spread_sheet_id)

    StockTimeSeries(alpha_vantage_id,'TSLA', 1).get()
    if CONFIG_SHEET and TRADE_SHEET and HISTORICAL_SHEET:
        ticker: Ticker = Ticker(GoogleSheet(config_spread_sheet_id), _ticker_callback)
        ticker.run()
