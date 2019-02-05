import logging
from sched import scheduler as Scheduler
from time import time, sleep
from pytz import timezone
from datetime import datetime

from typing import Dict, Optional, Any, List, Tuple, Union

from app.constants import CONFIG_PLACEMENT
from app.trader import Trader
from app.google.google_sheet import GoogleSheet

TIMEZONE: str = ''
OPENING_HOURS: str = ''
CLOSING_HOURS: str = ''
INTEVAL: int = 0

def get_trading_config(google_sheet: GoogleSheet) -> Optional[List[Any]]:
    global TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTEVAL

    values: Optional[List[List[Any]]] = google_sheet.read(
        CONFIG_PLACEMENT,
        major_dimension='COLUMNS'
    )

    if values:
        TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTEVAL = values[0]
        return values[0]
    
    return None

def analyze_price(historical_sheet: GoogleSheet) -> None:
    pass

def start_app(trade_spread_sheet_id: str, historical_spread_sheet_id: str) -> None:
    scheduler: Scheduler = Scheduler(time, sleep)

    trade_sheet: GoogleSheet = GoogleSheet(trade_spread_sheet_id)
    historical_sheet: GoogleSheet = GoogleSheet(historical_spread_sheet_id)

    get_trading_config(trade_sheet)

    def loop() -> None:
        analyze_price(historical_sheet)
        scheduler.enter(INTEVAL, 1, loop, ())

    if TIMEZONE and OPENING_HOURS and CLOSING_HOURS and INTEVAL:
        scheduler.enter(INTEVAL, 1, loop, ())
        scheduler.run()
