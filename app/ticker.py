import logging
from threading import Thread
from time import time, sleep
from sched import scheduler as Scheduler
from datetime import datetime as DateTime, date as Date
from pytz import timezone

from typing import Optional, List, Any, Callable, Union

from app.google.google_sheet import GoogleSheet, Result

class Ticker:
    
    _should_callback = False

    def __init__(self,
                 config_spread_sheet: GoogleSheet,
                 ticker_callbak: Callable[[DateTime, bool], Any]):

        self._ticker_callback: Callable[[DateTime, bool], Any] = ticker_callbak
        self._config_spread_sheet: GoogleSheet = config_spread_sheet
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
            self._should_callback: bool = \
                self._config_spread_sheet.read('B10').value(0, 0) == 'TRUE' and \
                self._current_date_time.weekday() < 5 and \
                self._current_date_time >= self._opening_hours and \
                self._current_date_time < self._closing_hours or True
            sleep(self._interval / 2)

    def _ticker(self) -> None:
        if self._should_callback:
            self._ticker_callback(self._current_date_time, True)

        self._scheduler.enter(self._interval, 1, self._ticker, ())

    def run(self) -> None:
        Thread(target=self.__ticker_thread).start()
       
        self._scheduler.enter(self._interval, 1, self._ticker, ())
        self._scheduler.run()
