
class TimeSeries:
    def __init__(self,
                 timestamp: str,
                 open: str,
                 close: str,
                 high: str,
                 low: str,
                 volume: str):

        self._timestamp: DateTime = DateTime.strptime(timestamp)
        self._open: float = float(open)
        self._close: float = float(close)
        self._high: float = float(high)
        self._low: float = float(low)
        self._volume: float = float(volume)
