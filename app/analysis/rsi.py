from numpy import nan
from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any, List

from app.analysis.technical_analysis import TechnicalAnalysis
from app.analysis.constants import RSI, RS, CLOSE, PERIODS, SPAN, PREV_AVG_GAIN, PREV_AVG_LOSS, AVG_GAIN, AVG_LOSS

class RsiAnalysis(TechnicalAnalysis):

    _current_average_gain: Optional[float] = None
    _current_average_loss: Optional[float] = None

    _rsi_columns: List[str] = [AVG_GAIN, AVG_LOSS, RS, RSI]

    def __init__(self, periods: int, span: int, config: Dict[str, Any] , data_frame: DataFrame):
 
        data_frame['AVG_GAIN'] = nan
        data_frame['AVG_LOSS'] = nan
        data_frame['RS'] = nan
        data_frame['RSI'] = nan
        
        super().__init__(config, data_frame)

        self._span = span

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

    def run_analysis(self) -> None:
        initial_average_gain, initial_average_loss = self._initialize_averages()
        initial_rs, initial_rsi = self._calculate_rsi(initial_average_gain, initial_average_loss)

        self._data_frame.loc[self._periods, self._rsi_columns] = \
            initial_average_gain, initial_average_loss, initial_rs, initial_rsi

        for index, (_, _, _, close, _, avg_gain, avg_loss, _, _) in self._data_frame[self._periods + 1:].iterrows():
            _, _, _, prev_close, _, prev_avg_gain, prev_avg_loss, _, _ = self._data_frame.iloc[index - 1]

            difference: float = prev_close - close
            avg_gain, avg_loss = self._calculate_averages(difference, prev_avg_gain, prev_avg_loss)
            rs, rsi = self._calculate_rsi(avg_gain, avg_loss)

            self._data_frame.loc[index, self._rsi_columns] = avg_gain, avg_loss, rs, rsi

    def return_values(self) -> Tuple[float, float, float, float, float, float, List[float]]:
        rsi_tail_df: DataFrame = self._data_frame.tail(4)[RSI]
        return self._return_quantative_values(self._span, rsi_tail_df)

def rsi_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)
    span: Optional[int] = config.get(SPAN)

    if periods and span:
        rsi: RsiAnalysis = RsiAnalysis(periods, span, config, data_frame)
        rsi.run_analysis()
        queue.put(rsi.return_values())
    else:
        raise Exception('RSI: Lacks appropriate settings to run RSI analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA

    queue: Queue = Queue(1)
    rsi_analysis(
        queue,
        {
            PERIODS: 14,
            SPAN: 4
        },
        TESLA
    );

    print(queue.get())

