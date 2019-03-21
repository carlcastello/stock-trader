import sys
from pandas import DataFrame
from numpy import where, polyfit
from math import acos, degrees

from queue import Queue

from typing import List, Dict, Any, Optional, Tuple

from app.analysis.technical_analysis import TechnicalAnalysis, ParametersNotCompleteException
from app.analysis.constants import MACD, MIN, MAX, CLOSE, SIGNAL, POSITION, SPAN

class MacdAnalysis(TechnicalAnalysis):

    _angle: Optional[float] = None
    _trend_df: Optional[DataFrame] = None

    _macd_columns = [MACD, SIGNAL, POSITION]

    def __init__(self,
                 macd_min: int,
                 macd_max: int,
                 macd_signal: int,
                 span: int,
                 config: Dict[str, Any],
                 data_frame: DataFrame) -> None:
        
        super().__init__(config, data_frame)
        
        self._macd_min: int = macd_min
        self._macd_max: int = macd_max
        self._macd_signal: int = macd_signal
        self._span = span

    def run_analysis(self) -> None:
        def _calculate_ewm(column: str, period: int) -> DataFrame:
            return self._data_frame[column].ewm(span=period).mean()

        self._data_frame[MACD] = \
            _calculate_ewm(CLOSE, self._macd_min) - _calculate_ewm(CLOSE, self._macd_max)
        self._data_frame[SIGNAL] = _calculate_ewm(MACD, self._macd_signal)

        self._data_frame[POSITION] = self._data_frame[MACD] >= self._data_frame[SIGNAL]

    def return_values(self) -> Dict[str, Any]:
        tail_df: DataFrame = self._data_frame[self._macd_columns].tail(self._span)        
        position_df = tail_df[POSITION]

        return {
            MACD: self._return_quantative_values(self._span, tail_df[MACD]),
            SIGNAL: self._return_quantative_values(self._span, tail_df[SIGNAL]),
            POSITION: (position_df.iloc[-1], position_df.iloc[-2], position_df.tolist())
        }

def macd_analysis(queue: Queue,
                  config: Dict[str, int],
                  data_frame: DataFrame) -> None:

    macd_min: Optional[int] = config.get(MIN)
    macd_max: Optional[int] = config.get(MAX)
    macd_signal: Optional[int] = config.get(SIGNAL)
    span: Optional[int] = config.get(SPAN)

    if macd_min and macd_max and macd_signal and span:
        macd: MacdAnalysis = MacdAnalysis(macd_min,
                                          macd_max,
                                          macd_signal,
                                          span,
                                          config,
                                          data_frame.copy())
        macd.run_analysis()     
        queue.put(macd.return_values())
    else:
        raise ParametersNotCompleteException('MACD: Lacks appropriate settings to run MACD analysis')

if __name__ == "__main__":
    import tkinter
    from matplotlib import pyplot
    from pylab import show
    from datetime import datetime as Datetime
    from app.analysis.mock_constants import TESLA

    should_plot: bool = False

    pyplot.close('all')

    figure, plot = pyplot.subplots()

    queue: Queue = Queue()

    macd_analysis(
        queue,
        {
            MIN: 8,
            MAX: 12,
            SIGNAL: 2,
        },
        TESLA
    )

    print(queue.get())
    
    if should_plot:
        figure.tight_layout()
        show()