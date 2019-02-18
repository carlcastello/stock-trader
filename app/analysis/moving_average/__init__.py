from typing import List

class MovingAverage:
    
    _points: List[float] = []

    def __init__(self, size: int):
        self._size: int = size
    
    def append(self, number: float) -> None:
        if len(self._points) == self._size:
            self._points.pop(0)
        self._points.append(number)

    def average(self) -> float:
        return sum(self._points) / len(self._points)
