from typing import Dict
from app.moving_average import MovingAverage
from app.moving_average.simple_moving_average import SimpleMovingAverage

SHORT = 'SHORT'
MEDIUM = 'MEDIUM'
LONG = 'LONG'

class Analysis:

    def __init__(self) -> None:
        self._moving_averages: Dict[str, MovingAverage] = {
            SHORT: SimpleMovingAverage(),
            MEDIUM: SimpleMovingAverage(),
            LONG: SimpleMovingAverage()
        }
