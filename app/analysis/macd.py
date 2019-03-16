from pandas import DataFrame
from numpy import where, polyfit
from math import acos, degrees

from queue import Queue

from typing import List, Dict, Any, Optional, Tuple

from app.analysis.technical_analysis import TechnicalAnalysis
from app.analysis.constants import BEARISH, BULLISH, CROSSOVER, SOARING, DIVERGING, RANGING, \
    CONVERGING, PLUMMETING, MACD, MACD_MIN, MACD_MAX, MACD_SIGNAL, REGRESSION_SPAN, CLOSE

class MacdAnalysis(TechnicalAnalysis):

    _angle: Optional[float] = None
    _trend_df: Optional[DataFrame] = None

    def __init__(self,
                 macd_min: int,
                 macd_max: int,
                 macd_signal: int,
                 regression_span: int,
                 config: Dict[str, Any],
                 data_frame: DataFrame) -> None:
        
        super().__init__(config, data_frame[CLOSE])
        
        self._macd_min: int = macd_min
        self._macd_max: int = macd_max
        self._macd_signal: int = macd_signal
        self._regression_span: int = regression_span

    @staticmethod
    def is_soaring(angle: float) -> bool:
        return 80 <= angle < 90

    @staticmethod
    def is_diverging(angle: float) -> bool:
        return 5 <= angle < 80
    
    @staticmethod
    def is_ranging(angle: float) -> bool:
        return -5 <= angle < 5
    
    @staticmethod
    def is_converging(angle: float) -> bool:
        return -80 <= angle < -5

    @staticmethod
    def is_plummeting(angle: float) -> bool:
        return -90 <= angle < -80

    def _calculate_trend(self) -> DataFrame:
        def _calculate_ewm(column: str, span: float) -> DataFrame:
            return self._data_frame.ewm(span=span).mean()

        macd_df = \
            _calculate_ewm(CLOSE, self._macd_min) - _calculate_ewm(CLOSE, self._macd_max)
        signal_df = _calculate_ewm(MACD, self._macd_signal)
        
        return macd_df > signal_df

    def _interpret_trend_angle(self, trend: str, angle: float) -> str:
        state: str = ''
        if self.is_ranging(angle):
            state = RANGING
        elif self.is_plummeting(angle):
            state = PLUMMETING
        elif self.is_soaring(angle):
            state = SOARING
        elif self.is_diverging(angle):
            state = DIVERGING if trend == BULLISH else CONVERGING
        elif self.is_converging(angle):
            state = CONVERGING if trend == BULLISH else DIVERGING

        return state

    @staticmethod
    def _interpret_trend(trend_df: DataFrame) -> str:
        length: int = len(trend_df.index)

        current_position: DataFrame = trend_df.iloc[length - 1]
        previous_position: DataFrame = trend_df.iloc[length - 2]

        trend: str = ''
        if current_position != previous_position:
            trend = CROSSOVER
        else:
            if current_position:
                trend = BULLISH
            else:
                trend = BEARISH
        return trend

    def run_analysis(self) -> None:
        self._trend_df = self._calculate_trend()
        self._angle: float = self._calculate_regression_angle(
            self._regression_span,
            self._data_frame.tail(self._regression_span)
        )
    
    def run_interpretor(self) -> Tuple[str, str]:
        if self._angle and self._trend_df is not None:
            trend: str = self._interpret_trend(self._trend_df)
            state: str = self._interpret_trend_angle(trend, self._angle)
            return trend, state
        else:
            raise Exception('MACD: "run_analysis" was unable to determine current averages')


def macd_analysis(result: Queue,
                  data_frame: DataFrame,
                  config: Dict[str, int],
                  **kwargs: str) -> None:

    macd_min: Optional[int] = config.get(MACD_MIN)
    macd_max: Optional[int] = config.get(MACD_MAX)
    macd_signal: Optional[int] = config.get(MACD_SIGNAL)

    regression_range:  Optional[int] = config.get(REGRESSION_SPAN)

    if macd_min and macd_max and macd_signal and regression_range:
        macd: MacdAnalysis = MacdAnalysis(macd_max,
                                          macd_max,
                                          macd_signal,
                                          regression_range,
                                          config,
                                          data_frame)
        macd.run_analysis()     
        result.put(macd.run_interpretor())
    else:
        raise Exception('MACD: Lacks appropriate settings to run MACD analysis')

if __name__ == "__main__":
    import tkinter
    from matplotlib import pyplot
    from pylab import show
    from datetime import datetime as Datetime
    from app.analysis.mock_constants import TESLA, TABLE_COLUMNS, MACD_SETTINGS

    should_plot: bool = False

    pyplot.close('all')

    figure, plot = pyplot.subplots()

    result: Queue = Queue()

    macd_analysis(
        result,
        DataFrame(TESLA, columns=TABLE_COLUMNS),
        MACD_SETTINGS,
        **{
            'should_plot': should_plot,
            'plot': plot,
            'figure': figure,
        }
    )

    print(result.get())
    
    if should_plot:
        figure.tight_layout()
        show()