from numpy import where
from pandas import DataFrame
from queue import Queue

from typing import Dict, Any, Optional

from app.analysis.constants import CLOSE, VOLUME, OBV, SPAN, MULTIPLIYER, BEARISH, BULLISH, POSITIVE, NEGATIVE
from app.analysis.technical_analysis import TechnicalAnalysis

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

        self._obv_slope = self._calulate_regression_slope(
            self._span,
            df_tail[OBV]
        )

        self._price_slope = self._calulate_regression_slope(
            self._span,
            df_tail[CLOSE]
        )

    def run_interpretor(self) -> str:
        if self._obv_slope is not None and self._price_slope is not None:
            if self._obv_slope > 0:
                # OBV: Upward movement
                if self._price_slope <= 0:
                    # PRICE: Downward movement
                    return BEARISH
                return POSITIVE 
            else:
                # OBV: Downward movement
                if self._price_slope > 0:
                    # PRICE: Upward Movement
                    return BULLISH
                return NEGATIVE
        else:
            raise Exception('OBV: "run_interpretor" was unable to determine current volume movements')

    def plot(self) -> None:
        if self._data_frame[OBV] is not None:
            self._plot(self._data_frame[OBV].tail(self._span))
        else:
            raise Exception('OBV: Lacks appropriate settings to plot OBV analysis')

def obv_analysis(queue: Queue,  config: Dict[str, Any], data_frame: DataFrame) -> None:
    regression_span: Optional[int] = config.get(SPAN)
    multipliyer: Optional[int] = config.get(MULTIPLIYER)

    if regression_span and multipliyer:
        obv: ObvAnalysis = ObvAnalysis(regression_span, multipliyer, config, data_frame)
        obv.run_analysis()
        queue.put(obv.run_interpretor())
        if config.get('should_plot'):
            obv.plot()
    else:
        raise Exception('OBV: Lacks appropriate settings to run OBV analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA, TABLE_COLUMNS

    queue: Queue = Queue(1)
    obv_analysis(
        queue,
        {
            SPAN: 10,
            MULTIPLIYER: 1000,
            'should_plot': True
        },
        DataFrame(TESLA, columns=TABLE_COLUMNS)
    )