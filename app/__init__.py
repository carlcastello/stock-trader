from sched import scheduler as Scheduler
from time import time, sleep

from typing import Dict, Optional, Any, List, Tuple

from app.google.google_sheet import GoogleSheet
from app.constants import CONFIG_PLACEMENT, TIMEZONE, OPENING_HOURS, CLOSING_HOURS, INTERVAL


SCHEDULER: Optional[Scheduler] = None 

CONFIG_SHEET: Optional[GoogleSheet] = None
TRADE_SHEET: Optional[GoogleSheet] = None
HISTORICAL_SHEET: Optional[GoogleSheet] = None

def _initialize_scheduler() -> None:
    global SCHEDULER

    SCHEDULER = Scheduler(time, sleep)    

def _initialize_sheet(config_spread_sheet_id: str,
                      trade_spread_sheet_id: str,
                      historical_spread_sheet_id: str) -> None:

    global CONFIG_SHEET, TRADE_SHEET, HISTORICAL_SHEET

    CONFIG_SHEET = GoogleSheet(config_spread_sheet_id)
    TRADE_SHEET = GoogleSheet(trade_spread_sheet_id)
    HISTORICAL_SHEET = GoogleSheet(historical_spread_sheet_id)

def _get_ticker_inteval() -> float: 
    if CONFIG_SHEET:
        interval_range: Optional[List[List[str]]] = CONFIG_SHEET.read(range='B7')
        if interval_range and interval_range[0] and interval_range[0][0]:
            try:
                return float(interval_range[0][0])
            except ValueError:
                pass
    return 60

def _ticker(interval: float) -> None:
    if CONFIG_SHEET and TRADE_SHEET and HISTORICAL_SHEET and SCHEDULER:
        SCHEDULER.enter(interval, 1, _ticker, (interval,))

def start_app(config_spread_sheet_id: str,
              trade_spread_sheet_id: str,
              historical_spread_sheet_id: str) -> None:

    _initialize_sheet(config_spread_sheet_id, trade_spread_sheet_id, historical_spread_sheet_id)

    if CONFIG_SHEET and TRADE_SHEET and HISTORICAL_SHEET:
        _initialize_scheduler()

        if SCHEDULER:
            interval: float = _get_ticker_inteval()        

            SCHEDULER.enter(interval, 1, _ticker, (interval,))
            SCHEDULER.run()
