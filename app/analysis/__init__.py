from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

try:
    from app.analysis.constants import MACD
    from app.analysis.macd import macd_analysis
    from app.analysis.rsi import rsi_analysis
except (ImportError, ModuleNotFoundError):
    from constants import MACD
    from macd import macd_analysis
    from rsi import rsi_analysis


def _create_thread(callable: Callable, *args: float) -> Tuple[Thread, Queue]:
    queue: Queue = Queue(1)
    thread: Thread = Thread(
        target=callable,
        args=(queue, *args)
    )
    return thread, queue

def analysis(now: Datetime,
             symbol: str,
             interval: float,
             time_stock_series_df: DataFrame,
             settings: Dict[str, Any]) -> None:

    macd_thread, macd_queue = _create_thread(
        macd_analysis,
        interval,
        time_stock_series_df.copy(),
        settings.get(MACD, {})
    )

    rsi_thread, rsi_queue = _create_thread(
        rsi_analysis,
        time_stock_series_df.copy()
    )

    macd_thread.start()
    rsi_thread.start()

    macd_thread.join()
    rsi_thread.join()

    print(macd_queue.get(), rsi_queue.get())

if __name__ == "__main__":
    from mock_constants import TESLA, TABLE_COLUMNS, MACD_SETTINGS
    analysis(
        Datetime.now(),
        'TSLA',
        60,
        DataFrame(TESLA, columns=TABLE_COLUMNS),
        {
            'MACD': MACD_SETTINGS
        }
    )
