from numpy import where
from pandas import DataFrame
from queue import Queue

from typing import Dict, Any, Optional, Tuple, List

from app.analysis.constants import CLOSE, VOLUME, OBV, SPAN, MULTIPLIER, BEARISH, BULLISH, POSITIVE, NEGATIVE, POSITION
from app.analysis.technical_analysis import TechnicalAnalysis, ParametersNotCompleteException

class ObvAnalysis(TechnicalAnalysis):

    _obv_slope: Optional[float] = None
    _price_slope: Optional[float] = None

    def __init__(self, _span: int, mutiplier: int, config: Dict[str, Any], data_frame: DataFrame) -> None: 
        super().__init__(config, data_frame[[CLOSE, VOLUME]].div(mutiplier))
        self._span = _span

    @staticmethod
    def _calulcate_obv_multiplier(price_difference: float) -> int:
        if price_difference > 0:
            return 1
        elif price_difference < 0:
            return -1
        else:
            return 0

    def run_analysis(self) -> None:
        multipliyer_df: DataFrame = self._data_frame[CLOSE].diff().fillna(0).apply(self._calulcate_obv_multiplier)
        self._data_frame[OBV] = (self._data_frame[VOLUME] * multipliyer_df).cumsum()

        df_tail: DataFrame = self._data_frame.tail(self._span)

    def run_interpretor(self) -> Dict[str, Tuple[float, float, float, float, float, float, float, List[float]]]:
        tail_df: DataFrame = self._data_frame.tail(self._span)
        return {
            OBV: self._return_quantative_values(self._span, tail_df[OBV])
        }

    def plot(self) -> None:
        if self._data_frame[OBV] is not None:
            self._plot(self._data_frame[OBV].tail(self._span))
        else:
            raise Exception('OBV: Lacks appropriate settings to plot OBV analysis')

def obv_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    regression_span: Optional[int] = config.get(SPAN)
    multiplier: Optional[int] = config.get(MULTIPLIER)

    if regression_span and multiplier:
        obv: ObvAnalysis = ObvAnalysis(regression_span, multiplier, config, data_frame.copy())
        obv.run_analysis()
        queue.put(obv.run_interpretor())
        if config.get('should_plot'):
            obv.plot()
    else:
        raise ParametersNotCompleteException('OBV: Lacks appropriate settings to run OBV analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA

    queue: Queue = Queue(1)
    obv_analysis(
        queue,
        {
            SPAN: 10,
            MULTIPLIER: 1000,
            'should_plot': True
        },
        TESLA
    )