from time import time, sleep
from sched import scheduler as Scheduler
from datetime import datetime as DateTime, date as Date
from pytz import timezone

from typing import Optional, List, Any, Callable

from app.google.google_sheet import GoogleSheet

class Ticker:

    def __init__(self,
                 config_spread_sheet: GoogleSheet,
                 ticker_callbak: Callable[[DateTime], Any]):

        self._ticker_callback: Callable[[DateTime], Any] = ticker_callbak
        self._config_spread_sheet: GoogleSheet = config_spread_sheet
        self._scheduler: Scheduler = Scheduler(time, sleep)

        timezone_result: Optional[List[List[Any]]] = self._config_spread_sheet.read('B2')
        if timezone_result and timezone_result[0] and timezone_result[0][0]:
            self._timezone = timezone(timezone_result[0][0])
            self._current_date_time: DateTime = DateTime.now(self._timezone)

        self.__long_term_update()
        self.__short_term_update()

    def __short_term_update(self) -> None:
        """
            Short Term Update == Update as frequent as posible 
        """
        self._current_date_time = DateTime.now(self._timezone)

        should_trade_result: Optional[List[List[str]]] = self._config_spread_sheet.read('B10')
        if should_trade_result and should_trade_result[0] and should_trade_result[0][0]: 
            self._should_trade = should_trade_result[0][0] == 'TRUE'




    def __long_term_update(self) -> None:
        """
            Long Term Update == Daily Updates
        """
        config: Optional[List[List[List[Any]]]] = self._config_spread_sheet.batch_read(
            ranges=['B3:B4', 'B7'],
            major_dimension='COLUMNS'
        )

        if config:
            trading_hours_value: List[List[str]] = config[0]
            if trading_hours_value and trading_hours_value[0] and len(trading_hours_value[0]) == 2:
                opening_hours: str = trading_hours_value[0][0]
                closing_hours: str = trading_hours_value[0][1]

                self._opening_hours: DateTime = DateTime.strptime(
                    f'{self._current_date_time.date()} {opening_hours}',
                    '%Y-%m-%d %I:%M %p'
                )
                self._closing_hours: DateTime = DateTime.strptime(
                    f'{self._current_date_time.date()} {closing_hours}',
                    '%Y-%m-%d %I:%M %p'
                )

            interval_value: List[List[str]] = config[1]
            if interval_value and interval_value[0] and interval_value[0][0]:
                try:
                    self._interval = float(interval_value[0][0])
                except ValueError:
                    self._interval = 60

    def _ticker(self) -> None:
        current_date_time: DateTime = DateTime.now(self._timezone)

        if self._current_date_time.date() != current_date_time.date():
            self.__long_term_update()

        self.__short_term_update()

        

        self._ticker_callback(self._current_date_time)

        self._scheduler.enter(self._interval, 1, self._ticker, ())

    def run(self) -> None:
        self._scheduler.enter(self._interval, 1, self._ticker, ())
        self._scheduler.run()
