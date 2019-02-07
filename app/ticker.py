from sched import scheduler as Scheduler
from time import time, sleep

from typing import Callable, Any

from app.constants import INTERVAL 


class Ticker:

    def __init__(self, ticker_callback: Callable[..., Any], **kwargs: str):
        self._scheduler: Scheduler = Scheduler(time, sleep)
        self._ticker_callback: Callable[..., Any] = ticker_callback
        try:
            self._interval: float = float(kwargs.get(INTERVAL, 60))
        except ValueError:
            self._interval: float = 60

    def _loop(self) -> None:
        self._ticker_callback()
        self._scheduler.enter(self._interval, 1, self._loop, ())

    def run(self) -> None:
        self._scheduler.enter(self._interval, 1, self._loop, ())
        self._scheduler.run()