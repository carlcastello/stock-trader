import logging
from threading import Thread
from time import time, sleep
from sched import scheduler as Scheduler
from datetime import datetime as DateTime, date as Date
from pytz import timezone

# from mypy.types. import KwArgs
from typing import Optional, List, Any, Callable, Union, Dict

from app.constants import INTERVAL, MACD
from app.google.google_sheet import GoogleSheet, Result

class Ticker:
    
    _should_callback = False
    _settings: Dict[str, Any] = {}

    def __init__(self,
                 config_spread_sheet_id: str,
                 ticker_callbak: Callable[[DateTime, float, Dict[str, Any]], None]):

        self._config_spread_sheet: GoogleSheet = GoogleSheet(config_spread_sheet_id)

        self._ticker_callback: Callable[[DateTime, float, Dict[str, Any]], Any] = ticker_callbak
        self._scheduler: Scheduler = Scheduler(time, sleep)

        results: List[Result] = self._config_spread_sheet.batch_read('B2', 'B7', 'B3:B4')

        self._timezone = timezone(results[0].value(0, 0))
        self._interval: float = float(results[1].value(0, 0))

        self._current_date_time: DateTime = DateTime.now(self._timezone)

        trading_hours: Result = results[2]
        self._opening_hours: DateTime = self.__create_datetime(trading_hours.value(0,0))
        self._closing_hours: DateTime = self.__create_datetime(trading_hours.value(1,0))
    
    def __create_datetime(self, hour: str) -> DateTime:
        return DateTime.strptime(
            f'{self._current_date_time.date()} {hour}',
            '%Y-%m-%d %I:%M %p'
        ).replace(tzinfo=self._timezone)

    def __ticker_thread(self) -> None:
        while True:
            self._current_date_time: DateTime = DateTime.now(self._timezone)
            should_callback: bool = \
                self._config_spread_sheet.read('B10').value(0, 0) == 'TRUE' and \
                self._current_date_time.weekday() < 5 and \
                self._current_date_time >= self._opening_hours and \
                self._current_date_time < self._closing_hours or True
            
            if not self._should_callback and should_callback:
                # Update config variables... occures once a day
                macd_config: Result = self._config_spread_sheet.read('B14:B16')
                self._settings = {
                    MACD: macd_config.column(0)
                }

            self._should_callback = should_callback
            sleep(self._interval / 2)

    def _ticker(self) -> None:
        if self._should_callback:
            self._ticker_callback(self._current_date_time, self._interval, self._settings)

        self._scheduler.enter(self._interval, 1, self._ticker, ())

    def run(self) -> None:
        Thread(target=self.__ticker_thread).start()
       
        self._scheduler.enter(self._interval, 1, self._ticker, ())
        self._scheduler.run()
