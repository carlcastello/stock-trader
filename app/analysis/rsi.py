from numpy import nan
from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any, List

from app.analysis.technical_analysis import TechnicalAnalysis
from app.analysis.constants import RSI, RS, CLOSE, PERIODS, PREV_AVG_GAIN, PREV_AVG_LOSS, AVG_GAIN, AVG_LOSS

class RsiAnalysis(TechnicalAnalysis):

    _current_average_gain: Optional[float] = None
    _current_average_loss: Optional[float] = None

    def __init__(self, periods: int, config: Dict[str, Any] , data_frame: DataFrame):
 
        data_frame['AVG_GAIN'] = nan
        data_frame['AVG_LOSS'] = nan
        data_frame['RS'] = nan
        data_frame['RSI'] = nan
        
        super().__init__(config, data_frame)
        
        self._periods: int = periods
        self._previous_periods: int = periods - 1

    def _initialize_averages(self) -> Tuple[float, float]:
        changes_df: DataFrame = self._data_frame[CLOSE].head(self._periods).diff()
        average_gain = changes_df[changes_df > 0].sum() / self._periods
        average_loss = changes_df[changes_df < 0].sum() / self._periods
        return average_gain, average_loss

    def _calculate_averages(self,
                            current_difference: float,
                            previous_average_gain: float,
                            previous_average_loss: float) -> Tuple[float, float]:
        gain: float = 0
        loss: float = 0

        if current_difference > 0:
            gain = current_difference
        elif current_difference < 0:
            loss = current_difference
        else:
            return previous_average_gain, previous_average_loss

        average_gain: float = ((previous_average_gain * self._previous_periods) + gain) / self._periods
        average_loss: float = ((previous_average_loss * self._previous_periods) + loss) / self._periods

        return average_gain, average_loss

    @staticmethod
    def _calculate_rsi(average_gain: float, average_loss: float) -> Tuple[float, float]:
        rs: float = abs(average_gain / average_loss)
        rsi: float = 100 - (100 / (1 + rs))
        return rs, rsi

    def run_analysis(self) -> None:
        initial_average_gain, initial_average_loss = self._initialize_averages()

        self._data_frame.loc[self._periods, [AVG_GAIN, AVG_LOSS, RS, RSI]] = \
            initial_average_gain, initial_average_loss, *self._calculate_rsi(initial_average_gain, initial_average_loss)

        for index, row in self._data_frame[self._periods + 1:].iterrows():
            current_difference: float = self._data_frame.loc[index - 1, CLOSE] - self._data_frame.loc[index, CLOSE] 
            average_gain, average_loss = \
                self._calculate_averages(current_difference, *self._data_frame.loc[index - 1, [AVG_GAIN, AVG_LOSS]])

            self._data_frame.loc[index, [AVG_GAIN, AVG_LOSS, RS, RSI]] = \
                average_gain, average_loss, *self._calculate_rsi(average_gain, average_loss)

    def return_values(self) -> Tuple[float, float, float, float, float, float, List[float]]:
        rsi_tail_df: DataFrame = self._data_frame.tail(4)[RSI]
        return self._return_quantative_values(rsi_tail_df)

def rsi_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)

    if periods:
        rsi: RsiAnalysis = RsiAnalysis(periods, config, data_frame)
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
            PERIODS: 14
        },
        TESLA
    );

    print(queue.get())

