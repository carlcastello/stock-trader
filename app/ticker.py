from time import time, sleep
from sched import scheduler as Scheduler
from datetime import datetime as DateTime

from typing import Optional, List, Any, Callable

from app.google.google_sheet import GoogleSheet

class Ticker:

    def __init__(self,
                 config_spread_sheet: GoogleSheet,
                 ticker_callbak: Callable[[DateTime], Any]):

        self._ticker_callback: Callable[[DateTime], Any] = ticker_callbak
        self._config_spread_sheet: GoogleSheet = config_spread_sheet
        self._scheduler: Scheduler = Scheduler(time, sleep)

        self._short_term_update()
        self._long_term_update()

    def _short_term_update(self) -> None:
        """
            Short Term Update == Update as frequent as posible 
        """
        pass

    def _long_term_update(self) -> None:
        """
            Long Term Update == Daily Updates
        """
        config: Optional[List[List[List[Any]]]] = self._config_spread_sheet.batch_read(ranges=['B3:B4', 'B7'], major_dimension='COLUMNS')

        if config:
            trading_hours_value: List[List[List[str]]] = config[0]
            if trading_hours_value and trading_hours_value[0]:
                print(trading_hours_value[0])
                

            interval_value: List[List[str]] = config[1]
            if interval_value and interval_value[0] and interval_value[0][0]:
                try:
                    self._interval = float(interval_value[0][0])
                except ValueError:
                    self._interval = 60

    def _ticker(self) -> None:
        self._ticker_callback(DateTime.now())
        self._scheduler.enter(self._interval, 1, self._ticker, ())

    def run(self) -> None:
        self._scheduler.enter(self._interval, 1, self._ticker, ())
        self._scheduler.run()
