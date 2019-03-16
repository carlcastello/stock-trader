from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

from app.google.google_sheet import GoogleSheet, Result
from app.analysis.constants import MACD, MIN, MAX, SIGNAL, SPAN, RSI, PERIODS, OBV
from app.analysis.macd import macd_analysis
from app.analysis.rsi import rsi_analysis


def _create_thread(callable: Callable, *args: Any) -> Tuple[Thread, Queue]:
    queue: Queue = Queue(1)
    thread: Thread = Thread(
        target=callable,
        args=(queue, *args)
    )
    return thread, queue

def _fetch_analysis_configs(queue: Queue, config_spread_sheet_id: str) -> None:
    configs: List[Result] = GoogleSheet(config_spread_sheet_id).batch_read('B14:B17', 'B20', 'B23')
    
    macd_configs: List[int] = list(map(int, configs[0].column(0)))
    rsi_configs: List[int] = list(map(int, configs[1].column(0)))
    obv_configs: List[int] = list(map(int, configs[2].column(0)))

    queue.put({
        MACD: {
            MIN: macd_configs[0],
            MAX: macd_configs[1],
            SIGNAL: macd_configs[2],
        },
        RSI: {
            PERIODS: rsi_configs[0]
        },
        OBV: {
            SPAN: obv_configs[0]
        }
    })

def analysis(now: Datetime,
             symbol: str,
             config_spread_sheet_id: str,
             time_stock_series_df: DataFrame) -> None:

    configs_thread, configs_queue = _create_thread(
        _fetch_analysis_configs,
        config_spread_sheet_id
    )

    configs_thread.start()
    configs: Dict[str, Any] = configs_queue.get()

    macd_thread, macd_queue = _create_thread(
        macd_analysis,
        configs.get(MACD, {}),
        time_stock_series_df.copy()
    )

    rsi_thread, rsi_queue = _create_thread(
        rsi_analysis,
        configs.get(RSI, {}),
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
