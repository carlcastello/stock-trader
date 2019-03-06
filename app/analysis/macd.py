from pandas import DataFrame
from numpy import where, polyfit
from math import acos, degrees

from queue import Queue

from typing import List, Dict, Any, Optional

if __name__ == "__main__":
    from constants import BEARISH, BULLISH, CROSSOVER, SOARING, DIVERGING, RANGING, \
        CONVERGING, PLUMMETING, MACD, MACD_MIN, MACD_MAX, MACD_SIGNAL, REGRESSION_RANGE, CLOSE
else:
    from app.analysis.constants import BEARISH, BULLISH, CROSSOVER, SOARING, DIVERGING, RANGING, \
        CONVERGING, PLUMMETING, MACD, MACD_MIN, MACD_MAX, MACD_SIGNAL, REGRESSION_RANGE, CLOSE

SIGNAL: str = 'SIGNAL'
TREND: str = 'TREND'

def _show_plot(data_frame: DataFrame, **kwargs: Any) -> None:
    plot_1 = kwargs.get('plot', '')
    plot_2 = plot.twinx()
    plot_3 = plot_2.twiny()

    red: str = 'red'
    blue: str = 'blue'
    black: str = 'black'
    orange: str = 'orange'
    pink: str = 'pink'

    plot_1.set_ylabel('Closing Price', color=black)
    plot_1.plot(data_frame[CLOSE], color=black)
    plot_1.tick_params(axis='y', labelcolor=black)

    plot_2.set_ylabel(MACD, color=red)
    plot_2.plot(data_frame[MACD], color=red)
    plot_2.tick_params(axis='y', labelcolor=red)

    plot_3.set_ylabel(SIGNAL, color=blue)
    plot_3.plot(data_frame[SIGNAL], color=blue)
    plot_3.tick_params(axis='y', labelcolor=blue)

def _identify_trend(macd_min: int,
                    macd_max: int,
                    macd_signal: int,
                    data_frame: DataFrame,) -> None:

    data_frame[MACD] = \
        data_frame[CLOSE].ewm(span=macd_min).mean() - \
        data_frame[CLOSE].ewm(span=macd_max).mean()

    data_frame[SIGNAL] = data_frame[MACD]\
        .ewm(span=macd_signal)\
        .mean()

    data_frame[TREND] = data_frame[MACD] > data_frame[SIGNAL]
 
def _interpret_trend(data_frame: DataFrame) -> str:
    length: int = len(data_frame.index)
    previous_index: int = length - 2
    current_index: int = length - 1

    current_position: DataFrame = data_frame.loc[current_index, TREND]
    previous_position: DataFrame = data_frame.loc[previous_index, TREND]

    trend: str = ''
    if current_position != previous_position:
        trend = CROSSOVER
    else:
        if current_position:
            trend = BULLISH
        else:
            trend = BEARISH
    return trend

def _identify_trend_angle(regression_range: int, data_frame: DataFrame) -> float:
    tail: DataFrame = data_frame.tail(regression_range)
    slope, _ = polyfit(range(regression_range), tail[CLOSE], 1)

    cosine_value: float = 0
    if slope > 0:
        cosine_value = regression_range/slope % 1
    elif slope < 0:
        cosine_value = -(regression_range/slope % 1)
    else:
        cosine_value = 0

    return degrees(acos(cosine_value))

def _interpret_state(trend: str, angle: float) -> str:
    def is_ranging() -> bool:
        return  angle >= -5 and angle < 5 

    def is_plummeting() -> bool:
        return angle >= -90 and angle < -80
    
    def is_soaring() -> bool:
        return angle >= 80 and angle < 90

    def is_diverging() -> bool:
        return angle >= 5 and angle < 80

    def is_converging() -> bool:
        return angle >= -80 and angle < -5

    state: str = ''
    if is_ranging():
        state = RANGING
    elif is_plummeting():
        state = PLUMMETING
    elif is_soaring():
        state = SOARING
    elif is_diverging():
        state = DIVERGING if trend == BULLISH else CONVERGING
    elif is_converging:
        state = CONVERGING if trend == BULLISH else DIVERGING
    return state

def macd_analysis(result: Queue,
                  interval: float,
                  data_frame: DataFrame,
                  settings: Dict[str, int],
                  **kwargs: str) -> None:

    macd_min: Optional[int] = settings.get(MACD_MIN)
    macd_max: Optional[int] = settings.get(MACD_MAX)
    macd_signal: Optional[int] = settings.get(MACD_SIGNAL)

    regression_range:  Optional[int] = settings.get(REGRESSION_RANGE)

    if macd_min and macd_max and macd_signal and regression_range:
        _identify_trend(macd_min, macd_max, macd_signal, data_frame)
        trend: str = _interpret_trend(data_frame)
        state: str = _interpret_state(trend, _identify_trend_angle(regression_range, data_frame))       
        result.put([trend, state])
    else:
        raise Exception('MACD: Lacks appropriate settings to run MACD analysis')

    if kwargs.get('should_plot', False):
        _show_plot(data_frame.tail(4), **kwargs)

if __name__ == "__main__":
    import tkinter
    from matplotlib import pyplot
    from pylab import show
    from datetime import datetime as Datetime
    from mock_constants import TESLA, TABLE_COLUMNS, MACD_SETTINGS

    should_plot: bool = True

    pyplot.close('all')

    figure, plot = pyplot.subplots()

    result: Queue = Queue()

    macd_analysis(
        result,
        60,
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