from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any

from app.analysis.technical_analysis import TechnicalAnalysis
from app.analysis.constants import CLOSE, PERIODS,PREVIOUS_AVERAGE_GAIN, PREVIOUS_AVERAGE_LOSS

class RsiAnalysis(TechnicalAnalysis):

    _current_average_gain: Optional[float] = None
    _current_average_loss: Optional[float] = None

    def __init__(self, periods: int, config: Dict[str, Any] , data_frame: DataFrame):
        super().__init__(config, data_frame[CLOSE].tail(periods).diff())
        
        self._periods: int = periods

    def _initialize_current_averages(self) -> Tuple[float, float]:
        average_gain = self._data_frame[self._data_frame > 0].sum() / self._periods
        average_loss = self._data_frame[self._data_frame < 0].sum() / self._periods

        return average_gain, average_loss

    def _calculate_current_averages(self,
                                    previous_average_gain: float,
                                    previous_average_loss: float) -> Tuple[float, float]:
        gain: float = 0
        loss: float = 0

        current_difference: float = self._data_frame.iloc[-1]
        previous_period: int = self._periods - 1 

        if current_difference > 0:
            gain = current_difference
        elif current_difference < 0:
            loss = current_difference
        else:
            return previous_average_gain, previous_average_loss

        average_gain: float = ((previous_average_gain * previous_period) + gain) / self._periods
        average_loss: float = ((previous_average_loss * previous_period) + loss) / self._periods

        return average_gain, average_loss

    def run_analysis(self) -> None:
        previous_average_gain = self._config.get(PREVIOUS_AVERAGE_GAIN)
        previous_average_loss = self._config.get(PREVIOUS_AVERAGE_LOSS)
        
        if previous_average_gain and previous_average_loss:
            self._current_average_gain, self._current_average_loss = self._calculate_current_averages(
                previous_average_gain,
                previous_average_loss
            )
        else: 
            self._current_average_gain, self._current_average_loss = self._initialize_current_averages()
        

    def run_interpreter(self) -> Tuple[float, float]:
        if self._current_average_gain and self._current_average_loss:
            relative_strength: float = abs(self._current_average_gain / self._current_average_loss)
            relative_strength_index:float = 100 - (100 / (1 + relative_strength))

            return relative_strength, relative_strength_index
        else:
            raise Exception('RSI: "run_analysis" was unabled to determine current averages')

def rsi_analysis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)

    if periods:
        rsi: RsiAnalysis = RsiAnalysis(periods, config, data_frame)
        rsi.run_analysis()
        queue.put(rsi.run_interpreter())
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
            [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28 ], #,  46.00],
            columns=[CLOSE]
        )
    );

    print(queue.get())


