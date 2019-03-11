from numpy import polyfit
from pandas import DataFrame

from typing import Any, Dict, Tuple

class TechnicalAnalysis: 

    def __init__(self, config: Dict[str, Any], data_frame: DataFrame) -> None:
        self._config = config
        self._data_frame = data_frame

    @staticmethod
    def _calculate_slope_intercept(span: int, data_frame: DataFrame) -> Tuple[float, float]:
        return polyfit(range(span), data_frame, 1) 

    def run_analysis(self) -> None:
        raise NotImplementedError()
    
    def run_interpreter(self) -> Any:
        raise NotImplementedError()
