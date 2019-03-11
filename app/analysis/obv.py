from numpy import where
from pandas import DataFrame
from queue import Queue

from typing import Dict, Any, Optional

from app.analysis.constants import CLOSE, VOLUME, OBV
from app.analysis.technical_analysis import TechnicalAnalysis

class ObvAnalysis(TechnicalAnalysis):

    _obv_df: Optional[DataFrame] = None

    def __init__(self, regression_span: int, config: Dict[str, Any], data_frame: DataFrame) -> None:
        super().__init__(config, data_frame[[CLOSE, VOLUME]])   
        self._regression_span = regression_span

    def run_analysis(self) -> None:
        multipliyer_df: DataFrame = where(self._data_frame[CLOSE].diff().fillna(0) >= 0, 1, -1)
        price_aware_df = self._data_frame[VOLUME] * multipliyer_df
        self._obv_df = price_aware_df.cumsum() 

    def run_interpreter(self) -> None:
        if self._obv_df is not None:
            print(self._obv_df)

def obv_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None: 
    obv: ObvAnalysis = ObvAnalysis(1, config, data_frame)
    obv.run_analysis()
    obv.run_interpreter()

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA, TABLE_COLUMNS

    queue: Queue = Queue(1)
    obv_analysis(queue, {}, DataFrame(TESLA, columns=TABLE_COLUMNS))