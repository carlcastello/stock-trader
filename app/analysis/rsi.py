from pandas import DataFrame
from queue import Queue

from typing import Tuple, Optional, Dict, Any

if __name__ == "__main__":
    from constants import CLOSE
else:
    from app.analysis.constants import CLOSE

CHANGE: str = 'CHANGE'
PREVIOUS_AVERAGE_GAIN: str = 'PREVIOUS_AVERAGES'
PREVIOUS_AVERAGE_LOSS: str = 'PREVIOUS_LOSS'


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

def _initialize_current_averages(periods: int, changes_df: DataFrame) -> Tuple[float, float]:
    average_gain = changes_df[changes_df > 0].sum() / periods
    average_loss = changes_df[changes_df < 0].sum() / periods

    return average_gain, average_loss

def rsi_analysis(queue: Queue, periods: int, settings: Dict[str, Any], data_frame: DataFrame) -> None:
    changes_df: DataFrame = data_frame[CLOSE].tail(periods).diff()

    previous_average_gain: Optional[float] = settings.get(PREVIOUS_AVERAGE_GAIN)
    previous_average_loss: Optional[float] = settings.get(PREVIOUS_AVERAGE_LOSS)
    
    current_average_gain: float = 0
    current_average_loss: float = 0
    if previous_average_gain and previous_average_loss:
        current_average_gain, current_average_loss = _calculate_current_averages(
            periods,
            changes_df.iloc[-1],
            previous_average_gain,
            previous_average_loss
        )
    else:
        current_average_gain, current_average_loss = _initialize_current_averages(
            periods,
            changes_df
        )


    relative_strength: float = abs(current_average_gain / current_average_loss)
    relative_strength_index:float = 100 - (100 / (1 + relative_strength))
    print(relative_strength, relative_strength_index)
    queue.put('RSI')


if __name__ == "__main__":
    from mock_constants import TESLA, TABLE_COLUMNS

    queue: Queue = Queue(1)
    rsi_analysis(
        queue,
        14,
        {
            PREVIOUS_AVERAGE_GAIN: 0.2385714285714283,
            PREVIOUS_AVERAGE_LOSS: -0.0999999999999999
        },
        DataFrame(
            [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28 ], #,  46.00],
            columns=[CLOSE]
        )
    );


