from datetime import datetime as DateTime

class TimeSeries:
    def __init__(self,
                 timestamp: str,
                 open: str,
                 high: str,
                 low: str,
                 close: str,
                 volume: str):

        self._timestamp: DateTime = DateTime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        self._open: float = float(open)
        self._close: float = float(close)
        self._high: float = float(high)
        self._low: float = float(low)
        self._volume: float = float(volume)
