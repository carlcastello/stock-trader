from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue, Empty
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

from app.google.google_sheet import GoogleSheet, Result
from app.slack.slack_trader_bot import SlackTraderBot 
from app.analysis.constants import MACD, MIN, MAX, SIGNAL, SPAN, RSI, PERIODS, OBV, MULTIPLIYER, ADX
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

def _fetch_analysis_configs(config_spread_sheet_id: str) -> Dict[str, Any]:
    configs: List[Result] = GoogleSheet(config_spread_sheet_id).batch_read('B14:B17', 'B20:B21', 'B24:B25', 'B28:B29')

    macd_configs: List[int] = list(map(int, configs[0].column(0)))
    rsi_configs: List[int] = list(map(int, configs[1].column(0)))
    obv_configs: List[int] = list(map(int, configs[2].column(0)))
    adx_configs: List[int] = list(map(int, configs[3].column(0)))

    return {
        MACD: {
            MIN: macd_configs[0],
            MAX: macd_configs[1],
            SIGNAL: macd_configs[2],
            SPAN: macd_configs[3]
        },
        RSI: {
            PERIODS: rsi_configs[0],
            SPAN: rsi_configs[1]
        },
        OBV: {
            SPAN: obv_configs[0],
            MULTIPLIYER: obv_configs[1]
        },
        ADX: {
            PERIODS: adx_configs[0],
            SPAN: adx_configs[1]
        }
    }

def _run_analysis(configs: Dict[str, Any], time_stock_series_df: DataFrame) -> Dict[str, Tuple]:

    macd_thread, macd_queue = _create_thread(macd_analysis, configs.get(MACD, {}), time_stock_series_df)
    rsi_thread, rsi_queue = _create_thread(rsi_analysis, configs.get(RSI, {}), time_stock_series_df)
    adx_thread, adx_queue = _create_thread(adx_analyis, configs.get(ADX, {}), time_stock_series_df)
    obv_thread, obv_queue = _create_thread(obv_analysis, configs.get(OBV, {}), time_stock_series_df)

    macd_thread.start()
    rsi_thread.start()
    obv_thread.start()
    adx_thread.start()

    return {
        **macd_queue.get(),
        **rsi_queue.get(),
        **obv_queue.get(),
        **adx_queue.get()
    }

def _interpret_analysis() -> str:
    return 'SELL'

def analysis(now: Datetime,
             symbol: str,
             config_spread_sheet_id: str,
             web_hook_url: str,
             time_stock_series_df: DataFrame) -> None:

    slack_trader_bot: SlackTraderBot = SlackTraderBot(symbol, web_hook_url)
    configs: Dict[str, Any] = _fetch_analysis_configs(config_spread_sheet_id)

    analysis_results: Dict[str, Tuple] = _run_analysis(configs, time_stock_series_df)
    suggestion: str = _interpret_analysis()

    slack_trader_bot.post(suggestion, analysis_results)

if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv
    
    from constants import COFING_SPREAD_SHEET_ID, WEB_HOOK_URL  
    from app.analysis.mock_constants import TESLA


    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.TSLA'))
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')
    web_hook_url: str = environ.get(WEB_HOOK_URL, '')

    analysis(
        Datetime.now(),
        'TSLA',
        config_spread_sheet_id,
        web_hook_url,
        TESLA
    )
