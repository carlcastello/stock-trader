from numpy import nan
from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any, List

from app.analysis.technical_analysis import TechnicalAnalysis
from app.analysis.constants import CLOSE, PERIODS,PREVIOUS_AVERAGE_GAIN, PREVIOUS_AVERAGE_LOSS

class RsiAnalysis(TechnicalAnalysis):

    _current_average_gain: Optional[float] = None
    _current_average_loss: Optional[float] = None

    def __init__(self, periods: int, config: Dict[str, Any] , data_frame: DataFrame):
 
        data_frame['CHANGES'] = data_frame.diff()
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

        self._data_frame.loc[self._periods, ['AVG_GAIN', 'AVG_LOSS', 'RS', 'RSI']] = \
            initial_average_gain, initial_average_loss, *self._calculate_rsi(initial_average_gain, initial_average_loss)

        for index, row in self._data_frame[self._periods + 1:].iterrows():
            average_gain, average_loss = \
                self._calculate_averages(row['CHANGES'], *self._data_frame.loc[index - 1, ['AVG_GAIN', 'AVG_LOSS']])

            self._data_frame.loc[index, ['AVG_GAIN', 'AVG_LOSS', 'RS', 'RSI']] = \
                average_gain, average_loss, *self._calculate_rsi(average_gain, average_loss)

    def return_values(self) -> Tuple[float, float, float, float, float, float, List[float]]:
        rsi_tail_df: DataFrame = self._data_frame.tail(4)['RSI']

        return (
            rsi_tail_df.iloc[-1], rsi_tail_df.iloc[-2], rsi_tail_df.min(), rsi_tail_df.max(),
            rsi_tail_df.mean(), self._calulate_regression_slope(4, rsi_tail_df), rsi_tail_df.tolist()
        )

def rsi_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)

    if periods:
        rsi: RsiAnalysis = RsiAnalysis(periods, config, data_frame)
        rsi.run_analysis()
        queue.put(rsi.return_values())
    else:
        raise Exception('RSI: Lacks appropriate settings to run RSI analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA, TABLE_COLUMNS

    queue: Queue = Queue(1)
    rsi_analysis(
        queue,
        {
            PERIODS: 14,
            PREVIOUS_AVERAGE_GAIN: 0.2385714285714283,
            PREVIOUS_AVERAGE_LOSS: -0.0999999999999999
        },
        DataFrame(
            [
                44.34, 44.09,
                44.15, 43.61,
                44.33, 44.83,
                45.10, 45.42,
                45.84, 46.08,
                45.89, 46.03,
                45.61, 46.28,
                46.28, 46.00,
                46.03, 46.41,
                46.22, 45.64,
                46.21, 46.25,
                45.71, 46.45,
                45.78, 45.35,
                44.03, 44.18,
                44.22, 44.57,
                43.42, 42.66
            ],
            columns=[CLOSE]
        )
    );

    print(queue.get())

