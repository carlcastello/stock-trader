from numpy import nan
from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any, List, Union

from app.analysis.technical_analysis import TechnicalAnalysis, ParametersNotCompleteException
from app.analysis.constants import RSI, RS, CLOSE, PERIODS, SPAN, PREV_AVG_GAIN, PREV_AVG_LOSS, AVG_GAIN, AVG_LOSS, \
    POSITION, OSC_MIN, OSC_MAX, OVER_BOUGHT, OVER_SOLD, RANGING

class RsiAnalysis(TechnicalAnalysis):

    _current_average_gain: Optional[float] = None
    _current_average_loss: Optional[float] = None

    _rsi_columns: List[str] = [AVG_GAIN, AVG_LOSS, RS, RSI, POSITION]

    def __init__(self, periods: int, osc_min: float, osc_max: float, span: int, config: Dict[str, Any] , data_frame: DataFrame):
 
        data_frame[AVG_GAIN] = nan
        data_frame[AVG_LOSS] = nan
        data_frame[RS] = nan
        data_frame[RSI] = nan
        data_frame[POSITION] = False
        
        super().__init__(config, data_frame)

        self._span = span

        self._osc_max: float = osc_max
        self._osc_min: float = osc_min
        self._periods: int = periods
        self._prev_periods: int = periods - 1

    def _initialize_averages(self) -> Tuple[float, float]:
        changes_df: DataFrame = self._data_frame[CLOSE].head(self._periods).diff()
        avg_gain = changes_df[changes_df > 0].sum() / self._periods
        avg_loss = changes_df[changes_df < 0].sum() / self._periods
        return avg_gain, avg_loss

    def _calculate_averages(self,
                            difference: float,
                            prev_avg_gain: float,
                            prev_avg_loss: float) -> Tuple[float, float]:
        gain: float = 0
        loss: float = 0

        if difference > 0:
            gain = difference
        elif difference < 0:
            loss = difference
        else:
            return prev_avg_gain, prev_avg_loss

        average_gain: float = ((prev_avg_gain * self._prev_periods) + gain) / self._periods
        average_loss: float = ((prev_avg_loss * self._prev_periods) + loss) / self._periods

        return average_gain, average_loss

    @staticmethod
    def _calculate_rsi(avg_gain: float, avg_loss: float) -> Tuple[float, float]:
        rs: float = abs(avg_gain / avg_loss)
        rsi: float = 100 - (100 / (1 + rs))
        return rs, rsi

    def _calculate_position(self, rsi: float) -> str:
        if rsi <= self._osc_min:
            return OVER_SOLD
        elif rsi >= self._osc_max:
            return OVER_BOUGHT
        else:
            return RANGING

    def run_analysis(self) -> None:
        initial_average_gain, initial_average_loss = self._initialize_averages()
        initial_rs, initial_rsi = self._calculate_rsi(initial_average_gain, initial_average_loss)

        self._data_frame.loc[self._periods, self._rsi_columns] = \
            initial_average_gain, initial_average_loss, initial_rs, initial_rsi, self._calculate_position(initial_rsi)

        for index, (_, _, _, close, _, avg_gain, avg_loss, _, _, _) in self._data_frame[self._periods + 1:].iterrows():
            _, _, _, prev_close, _, prev_avg_gain, prev_avg_loss, _, _, _ = self._data_frame.iloc[index - 1]

            difference: float = prev_close - close
            avg_gain, avg_loss = self._calculate_averages(difference, prev_avg_gain, prev_avg_loss)
            rs, rsi = self._calculate_rsi(avg_gain, avg_loss)

            self._data_frame.loc[index, self._rsi_columns] = avg_gain, avg_loss, rs, rsi, self._calculate_position(rsi)

    def return_values(self) -> Dict[str, Union[Tuple[float, float, float, float, float, float, float, List[float]], Tuple[bool, bool]]]:
        tail_df: DataFrame = self._data_frame.tail(self._span)
        position_df: DataFrame = tail_df[POSITION]
        return {
            RSI: self._return_quantative_values(self._span, tail_df[RSI]),
            POSITION: (position_df.iloc[-1], position_df.iloc[-2])
        }

def rsi_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)
    span: Optional[int] = config.get(SPAN)
    osc_min: Optional[float] = config.get(OSC_MIN)
    osc_max: Optional[float] = config.get(OSC_MAX)

    if periods and span and osc_min and osc_max:
        rsi: RsiAnalysis = RsiAnalysis(periods, osc_min, osc_max, span, config, data_frame.copy())
        rsi.run_analysis()
        queue.put(rsi.return_values())
    else:
        raise ParametersNotCompleteException('RSI: Lacks appropriate settings to run RSI analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA

    queue: Queue = Queue(1)
    rsi_analysis(
        queue,
        {
            PERIODS: 14,
            SPAN: 4,
            OSC_MAX: 70,
            OSC_MIN: 30
        },
        TESLA
    );

    print(queue.get())

