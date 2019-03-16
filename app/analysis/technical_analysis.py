from math import acos, degrees
from numpy import polyfit
from pandas import DataFrame
from matplotlib import pyplot

from typing import Any, Dict, Tuple


class TechnicalAnalysis: 

    def __init__(self, config: Dict[str, Any], data_frame: DataFrame) -> None:
        self._config = config
        self._data_frame = data_frame

    @staticmethod
    def _calulate_regression_slope(span: int, data_frame: DataFrame) -> float:
        return polyfit(range(span), data_frame, 1)[0]

    def _calculate_regression_angle(self, span: int, data_frame: DataFrame) -> float:
        slope: float = self._calculate_regression_angle(span, data_frame)

        cosine_value: float = 0
        if slope > 0:
            cosine_value = (span / slope) % 1
        elif slope < 0:
            cosine_value = -(span / slope % 1)
        else:
            cosine_value = 0

        return degrees(acos(cosine_value))

    def _plot(self, data_frame: DataFrame) -> None:
        data_frame.plot()
        pyplot.show()

    def run_analysis(self) -> None:
        raise NotImplementedError()
    
    def return_values(self) -> Any:
        raise NotImplementedError()
