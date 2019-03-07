from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

from app.google.google_sheet import GoogleSheet, Result
from app.analysis.constants import MACD, MACD_MIN, MACD_MAX, MACD_SIGNAL, REGRESSION_RANGE, RSI, PERIODS
from app.analysis.macd import macd_analysis
from app.analysis.rsi import rsi_analysis


def _create_thread(callable: Callable, *args: Any) -> Tuple[Thread, Queue]:
    queue: Queue = Queue(1)
    thread: Thread = Thread(
        target=callable,
        args=(queue, *args)
    )
    return thread, queue

def _fetch_analysis_settings(queue: Queue, config_spread_sheet_id: str) -> None:
    settings: List[Result] = GoogleSheet(config_spread_sheet_id).batch_read('B14:B17', 'B20')
    
    macd_settings: List[int] = list(map(int, settings[0].column(0)))
    rsi_settings: List[int] = list(map(int, settings[1].column(0)))

    queue.put({
        MACD: {
            MACD_MIN: macd_settings[0],
            MACD_MAX: macd_settings[1],
            MACD_SIGNAL: macd_settings[2],
            REGRESSION_RANGE: macd_settings[3],
        },
        RSI: {
            PERIODS: rsi_settings[0]
        }
    })

def analysis(now: Datetime,
             symbol: str,
             config_spread_sheet_id: str,
             time_stock_series_df: DataFrame) -> None:

    settings_thread, settings_queue = _create_thread(
        _fetch_analysis_settings,
        config_spread_sheet_id
    )

    settings_thread.start()
    settings: Dict[str, Any] = settings_queue.get()

    macd_thread, macd_queue = _create_thread(
        macd_analysis,
        time_stock_series_df.copy(),
        settings.get(MACD, {})
    )

    rsi_thread, rsi_queue = _create_thread(
        rsi_analysis,
        settings.get(RSI, {}),
        time_stock_series_df.copy()
    )

    macd_thread.start()
    rsi_thread.start()

    macd_thread.join()
    rsi_thread.join()

    print(macd_queue.get(), rsi_queue.get())

if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv
    
    from constants import COFING_SPREAD_SHEET_ID    
    from app.analysis.mock_constants import TESLA, TABLE_COLUMNS, MACD_SETTINGS

    dotenv_path = path.join(path.dirname(__file__), f'../../env/.TSLA')
    load_dotenv(dotenv_path)
    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')

    analysis(
        Datetime.now(),
        'TSLA',
        environ.get(COFING_SPREAD_SHEET_ID, ''),
        DataFrame(TESLA, columns=TABLE_COLUMNS)
    )
