import logging
from threading import Thread
from time import time, sleep
from sched import scheduler as Scheduler
from datetime import datetime as DateTime, date as Date
from pytz import timezone
from pyrebase.pyrebase import Auth

from typing import Optional, List, Any, Callable, Union, Dict, Tuple

from app.constants import TICKER, TIMEZONE, INTERVAL, OPENING_HOURS, CLOSING_HOURS, SHOULD_TRADE
from app.google.google_sheet import GoogleSheet, Result

class Ticker:
     
    _should_callback = False

    def __init__(self,
                 symbol: str,
                 firebase: Tuple[Auth, Any, str, str],
                 ticker_callbak: Callable[[DateTime, str], None]):

        self._symbol: str = symbol
        self._auth, self._db, self._auth_token, self._refresh_token = firebase

        self._ticker_callback: Callable[[DateTime, str], Any] = ticker_callbak
        self._scheduler: Scheduler = Scheduler(time, sleep)

        values: Dict[str, Any] = self._db.child(f'{symbol}/{TICKER}').get(self._auth_token).val()

        self._timezone = timezone(values[TIMEZONE])
        self._interval: float = float(values[INTERVAL]) 

        self._current_date_time: DateTime = DateTime.now(self._timezone)

        self._opening_hours: DateTime = self.__create_datetime(values[OPENING_HOURS])
        self._closing_hours: DateTime = self.__create_datetime(values[CLOSING_HOURS])

    def __create_datetime(self, hour: str) -> DateTime:
        time = f'{self._current_date_time.date()} {hour}' 
        return self._timezone.localize(DateTime.strptime(time, '%Y-%m-%d %I:%M %p'))

    def __update_class_variables(self) -> None:
        prev_date_time = self._current_date_time
        self._current_date_time: DateTime = DateTime.now(self._timezone)

        if prev_date_time.hour != self._current_date_time.hour:
            user: Dict[str, str] = self._auth.refresh(self._refresh_token)
            self._auth_token = user['idToken']
            self._refresh_token = user['refreshToken']

    def __ticker_thread(self) -> None:
        while True:
            self.__update_class_variables()
            self._should_callback: bool = \
                self._db.child(f'{self._symbol}/{SHOULD_TRADE}').get(self._auth_token).val() and \
                self._current_date_time.weekday() < 5 and \
                self._opening_hours <= self._current_date_time < self._closing_hours
                
            sleep(self._interval / 2)

    def _ticker(self) -> None:
        if self._should_callback:
            self._ticker_callback(self._current_date_time, self._auth_token)

        self._scheduler.enter(self._interval, 1, self._ticker, ())

    def run(self) -> None:
        Thread(target=self.__ticker_thread).start()
       
        self._scheduler.enter(self._interval, 1, self._ticker, ())
        self._scheduler.run()
