from pandas import DataFrame
from numpy import where

from queue import Queue

from typing import List, Dict, Any

try: 
    from app.constants import MACD
    from app.analysis.constants import BEARISH, BULLISH
except (ImportError, ModuleNotFoundError):
    MACD = 'MACD' 
    BEARISH = 'BEARISH'
    BULLISH = 'BULLISH'


def macd_plot(data_frame: DataFrame, **kwargs: Any) -> None:
    plot_1 = kwargs.get('plot', '')
    plot_2 = plot.twinx()
    plot_3 = plot_2.twinx()
    plot_4 = plot_2.twinx()
    plot_5 = plot_2.twinx()

    red: str = 'red'
    blue: str = 'blue'
    black: str = 'black'
    orange: str = 'orange'
    pink: str = 'pink'


    plot_1.set_ylabel('Closing Price', color=black)
    plot_1.plot(data_frame['4. close'], color=black)
    plot_1.tick_params(axis='y', labelcolor=black)

    plot_2.set_ylabel('MACD', color=red)
    plot_2.plot(data_frame['macd'], color=red)
    plot_2.tick_params(axis='y', labelcolor=red)

    plot_3.set_ylabel('Signal', color=blue)
    plot_3.plot(data_frame['signal'], color=blue)
    plot_3.tick_params(axis='y', labelcolor=blue)

    # plot_4.set_ylabel('Swing', color=orange)
    # plot_4.plot(data_frame['swing'], color=orange)
    # plot_4.tick_params(axis='y', labelcolor=orange)

    # plot_5.set_ylabel('Swing', color=pink)
    # plot_5.plot(data_frame['swing_signal'], color=pink)
    # plot_5.tick_params(axis='y', labelcolor=pink)

def check_settings(settings: List[int]) -> List[int]:
    if len(settings) == 3:
        return settings
    else:
        raise Exception('MACD: Lacks appropriate settings to run MACD analysis')

def macd_analysis(result: Queue, data_frame: DataFrame, settings: List[int], **kwargs: str) -> None:
    columns: List[str] = ['4. close']
    macd_min, macd_max, macd_signal = check_settings(settings)

    data_frame['macd'] = \
        data_frame[columns].ewm(span=macd_min).mean() - \
        data_frame[columns].ewm(span=macd_max).mean()

    data_frame['signal'] = data_frame['macd']\
        .ewm(span=macd_signal)\
        .mean()

    data_frame['position'] = data_frame['macd'] > data_frame['signal']

    if kwargs.get('should_plot', False):
        macd_plot(data_frame, **kwargs)



    result.put(BEARISH if data_frame['position'].tail(1).bool() else BULLISH)


if __name__ == "__main__":
    import tkinter
    from matplotlib import pyplot
    from pylab import show
    from datetime import datetime as Datetime

    pyplot.close('all')

    tesla = [
        (306.88, 306.88, 306.77, 306.81, 4272.0),
        (306.7748, 306.7748, 306.57, 306.57, 2083.0),
        (306.54, 306.7, 306.54, 306.655, 3018.0),
        (306.7, 306.7, 306.66, 306.66, 1058.0),
        (306.78, 306.84, 306.78, 306.84, 3418.0),
        (306.88, 306.88, 306.6842, 306.6842, 3504.0),
        (306.8198, 306.86, 306.8198, 306.86, 1646.0),
        (306.85, 306.8653, 306.82, 306.82, 2774.0),
        (306.95, 307.0, 306.91, 306.91, 3407.0),
        (306.9, 306.9, 306.75, 306.8, 3304.0),
        (306.87, 306.87, 306.68, 306.68, 6849.0),
        (306.87, 306.87, 306.8, 306.8, 1753.0),
        (306.78, 306.78, 306.74, 306.74, 1240.0),
        (306.83, 306.85, 306.79, 306.85, 2395.0),
        (306.76, 306.91, 306.76, 306.91, 2669.0),
        (306.91, 306.98, 306.91, 306.98, 2357.0),
        (306.93, 306.93, 306.93, 306.93, 631.0),
        (306.98, 306.99, 306.91, 306.91, 9688.0),
        (306.79, 306.88, 306.79, 306.88, 2533.0),
        (306.92, 306.92, 306.88, 306.88, 828.0),
        (306.92, 306.92, 306.89, 306.89, 1582.0),
        (306.8672, 306.8672, 306.7503, 306.7718, 4944.0),
        (306.83, 306.8658, 306.83, 306.8658, 2378.0),
        (306.855, 306.89, 306.75, 306.89, 6680.0),
        (306.9, 306.96, 306.9, 306.92, 8806.0),
        (306.8939, 307.0, 306.8939, 307.0, 1330.0),
        (306.9, 306.97, 306.9, 306.97, 1979.0),
        (306.94, 307.01, 306.94, 307.0, 14152.0),
        (307.02, 307.1, 306.99, 307.1, 9374.0),
        (307.0212, 307.0212, 307.0, 307.0, 3431.0),
        (307.09, 307.1, 307.05, 307.05, 5096.0),
        (307.0, 307.0, 306.871, 306.871, 4289.0),
        (306.909, 306.909, 306.909, 306.909, 1214.0),
        (306.89, 306.98, 306.81, 306.98, 4237.0),
        (306.97, 306.97, 306.97, 306.97, 1443.0),
        (306.87, 306.87, 306.75, 306.76, 9444.0),
        (306.79, 306.79, 306.68, 306.7632, 5888.0),
        (306.69, 306.69, 306.47, 306.5, 9689.0),
        (306.63, 306.7, 306.63, 306.7, 2227.0),
        (306.75, 306.86, 306.73, 306.8, 5791.0),
        (306.83, 306.83, 306.76, 306.76, 2870.0),
        (306.72, 306.85, 306.69, 306.69, 14698.0),
        (306.8, 306.82, 306.729, 306.82, 5201.0),
        (306.8, 306.8, 306.67, 306.73, 4259.0),
        (306.86, 306.8976, 306.8206, 306.8206, 7716.0),
        (306.87, 306.93, 306.71, 306.73, 6297.0),
        (306.88, 306.88, 306.73, 306.73, 1920.0),
        (306.8, 306.8, 306.7, 306.7, 2763.0),
        (306.745, 306.81, 306.745, 306.81, 2304.0),
        (306.805, 306.805, 306.7732, 306.7732, 2222.0),
        (306.72, 306.72, 306.72, 306.72, 1009.0),
        (306.71, 306.71, 306.6, 306.63, 7195.0),
        (306.61, 306.67, 306.61, 306.64, 3414.0),
        (306.64, 306.64, 306.5, 306.5, 6781.0),
        (306.4, 306.4889, 306.39, 306.4889, 25949.0),
        (306.51, 306.51, 306.4169, 306.42, 5048.0),
        (306.4797, 306.4982, 306.4032, 306.404, 9554.0),
        (306.49, 306.49, 306.43, 306.44, 2340.0),
        (306.37, 306.47, 306.37, 306.47, 1861.0),
        (306.45, 306.45, 306.385, 306.45, 7247.0),
        (306.54, 306.7, 306.54, 306.58, 14538.0),
        (306.6718, 306.6718, 306.59, 306.59, 4968.0),
        (306.59, 306.66, 306.59, 306.66, 3595.0),
        (306.63, 306.67, 306.57, 306.67, 4874.0),
        (306.57, 306.63, 306.57, 306.63, 7907.0),
        (306.67, 306.69, 306.6425, 306.6425, 5079.0),
        (306.68, 306.79, 306.68, 306.79, 5913.0),
        (306.83, 306.905, 306.83, 306.905, 6416.0),
        (306.92, 306.92, 306.87, 306.87, 5467.0),
        (306.83, 306.905, 306.83, 306.88, 6331.0),
        (306.84, 306.84, 306.8, 306.84, 7762.0),
        (306.84, 306.99, 306.83, 306.99, 11457.0),
        (306.99, 307.11, 306.99, 307.03, 17084.0),
        (307.03, 307.06, 306.94, 306.99, 7542.0),
        (307.1, 307.1, 307.03, 307.03, 6566.0),
        (307.04, 307.28, 307.04, 307.23, 13682.0),
        (307.26, 307.53, 307.26, 307.53, 14863.0),
        (307.45, 307.54, 307.4, 307.5395, 9224.0),
        (307.56, 307.56, 307.26, 307.3, 11444.0),
        (307.37, 307.37, 306.9687, 307.0, 14640.0),
        (307.04, 307.0973, 306.93, 306.953, 13184.0),
        (306.9659, 307.01, 306.94, 306.98, 5295.0),
        (306.99, 307.05, 306.9, 307.05, 8729.0),
        (307.01, 307.03, 306.97, 306.97, 6662.0),
        (306.99, 307.0, 306.99, 307.0, 4790.0),
        (307.01, 307.1, 306.98, 307.04, 13009.0),
        (307.13, 307.33, 307.11, 307.33, 9656.0),
        (307.37, 307.8, 307.37, 307.8, 33168.0),
        (307.81, 307.81, 307.68, 307.7, 24481.0),
        (307.635, 307.69, 307.42, 307.51, 9647.0),
        (307.44, 307.47, 307.19, 307.195, 13493.0),
        (307.27, 307.42, 307.27, 307.39, 19736.0),
        (307.37, 307.58, 307.37, 307.56, 17281.0),
        (307.57, 307.84, 307.46, 307.78, 21921.0),
        (307.75, 307.75, 307.53, 307.59, 13950.0),
        (307.57, 307.87, 307.57, 307.79, 38869.0),
        (307.85, 307.94, 307.81, 307.81, 52476.0),
        (307.79, 307.9, 307.79, 307.87, 39769.0),
        (307.83, 307.9101, 307.76, 307.78, 42773.0),
        (307.81, 307.95, 307.7276, 307.8, 66061.0),
    ]

    figure, plot = pyplot.subplots()

    result:Queue = Queue()

    macd_analysis(
        result,
        DataFrame(tesla, columns=['1. open', '2. high', '3. low', '4. close', '5. volume']),
        [3, 9, 10],
        **{
            'should_plot': True,
            'plot': plot,
            'figure': figure,
        }
    )
    
    figure.tight_layout()
    show()