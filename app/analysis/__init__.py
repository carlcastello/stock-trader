from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue, Empty
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

from app.google.google_sheet import GoogleSheet, Result
from app.analysis.constants import MACD, MIN, MAX, SIGNAL, SPAN, RSI, PERIODS, OBV, ADX
from app.analysis.macd import macd_analysis
from app.analysis.rsi import rsi_analysis
from app.analysis.obv import obv_analysis
from app.analysis.adx import adx_analyis
from app.analysis.technical_analysis import ParametersNotCompleteException


def _create_thread(callable: Callable, *args: Any) -> Tuple[Thread, Queue]:
    queue: Queue = Queue(1)
    thread: Thread = Thread(
        target=callable,
        args=(queue, *args)
    )
    return thread, queue

def _fetch_analysis_configs(queue: Queue, config_spread_sheet_id: str) -> None:
    configs: List[Result] = GoogleSheet(config_spread_sheet_id).batch_read('B14:B17', 'B20:B21', 'B24:B25')
    
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

def handle_result(queue: Queue) -> Optional[Any]:
    try:
        result = queue.get(block=False)
    except Empty:
        exc_type, exc_obj, exc_trace = result
        print(exc_trace, exc_obj, exc_trace)
    else:
       return result

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
        time_stock_series_df
    )

    rsi_thread, rsi_queue = _create_thread(
        rsi_analysis,
        configs.get(RSI, {}),
        time_stock_series_df
    )

    obv_thread, obv_queue = _create_thread(
        obv_analysis,
        configs.get(OBV, {}),
        time_stock_series_df
    )

    adx_thread, adx_queue = _create_thread(
        adx_analyis,
        configs.get(ADX, {}),
        time_stock_series_df
    )

    macd_thread.start()
    rsi_thread.start()
    obv_thread.start()
    adx_thread.start()

    macd_queue.get(block=False)
    rsi_queue.get(block=False)
    obv_queue.get(block=False)
    adx_queue.get(block=False)

# /    try:
    #     # macd_queue.get()
    #     # rsi_queue.get()
    #     # obv_queue.get()
    #     # adx_queue.get()
    # except ParametersNotCompleteException as exception:
    #     # macd_thread.join()
    #     # rsi_thread.join()
    #     # obv_thread.join()
    #     # adx_thread.join()
    #     print('-----------------------------------------------------------------')
    #     raise exception
    # else:
    #     pass
        # print(macd_queue.get(), rsi_queue.get())

if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv
    
    from constants import COFING_SPREAD_SHEET_ID    
    from app.analysis.mock_constants import TESLA

    dotenv_path = path.join(path.dirname(__file__), f'../../env/.TSLA')
    load_dotenv(dotenv_path)
    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')

    analysis(
        Datetime.now(),
        'TSLA',
        environ.get(COFING_SPREAD_SHEET_ID, ''),
        TESLA
    )
