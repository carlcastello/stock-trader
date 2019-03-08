from pandas import DataFrame

from typing import Any, Dict

class TechnicalAnalysis: 

    def __init__(self, config: Dict[str, Any], data_frame: DataFrame) -> None:
        self._config = config
        self._data_frame = data_frame

    def run_analysis(self) -> None:
        raise NotImplementedError()
    
    def calculate_return_values(self) -> Any:
        raise NotImplementedError()
