from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any

from app.analysis.constants import CLOSE, PERIODS,PREVIOUS_AVERAGE_GAIN, PREVIOUS_AVERAGE_LOSS

CHANGE: str = 'CHANGE'

def _initialize_current_averages(periods: int, changes_df: DataFrame) -> Tuple[float, float]:
    average_gain = changes_df[changes_df > 0].sum() / periods
    average_loss = changes_df[changes_df < 0].sum() / periods

    return average_gain, average_loss

def _calculate_current_averages(periods: int,
                                current_difference: float,
                                previous_average_gain: float,
                                previous_average_loss: float) -> Tuple[float, float]:

    gain: float = 0
    loss: float = 0
    average_gain: float = 0
    average_loss: float = 0
    previous_period: int = periods - 1 

    if current_difference > 0:
        gain = current_difference
    elif current_difference < 0:
        loss = current_difference
    else:
        return previous_average_gain, previous_average_loss

    average_gain = ((previous_average_gain * previous_period) + gain) / periods
    average_loss = ((previous_average_loss * previous_period) + loss) / periods

    return average_gain, average_loss

def _calculate_current_gain_and_current_loss(periods: int,
                                             previous_average_gain: Optional[float],
                                             previous_average_loss: Optional[float],
                                             data_frame: DataFrame ) -> Tuple[float, float]:
    changes_df: DataFrame = data_frame[CLOSE].tail(periods).diff()
    
    if previous_average_gain and previous_average_loss:
        return _calculate_current_averages(
            periods,
            changes_df.iloc[-1],
            previous_average_gain,
            previous_average_loss
        )
    else:
        return _initialize_current_averages(
            periods,
            changes_df
        )

def rsi_analysis(queue: Queue, settings: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = settings.get(PERIODS)

    if periods:
        changes_df: DataFrame = data_frame[CLOSE].tail(periods).diff()
      
        current_average_gain, current_average_loss = _calculate_current_gain_and_current_loss(
            periods,
            settings.get(PREVIOUS_AVERAGE_GAIN),
            settings.get(PREVIOUS_AVERAGE_LOSS),
            data_frame
        )

        relative_strength: float = abs(current_average_gain / current_average_loss)
        relative_strength_index:float = 100 - (100 / (1 + relative_strength))

        queue.put([relative_strength, relative_strength_index])
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


