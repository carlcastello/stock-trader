from datetime import datetime as Datetime
from pandas import DataFrame
from queue import Queue, Empty
from threading import Thread

from typing import Optional, List, Dict, Any, Tuple, Callable

from app.google.google_sheet import GoogleSheet, Result
from app.slack.slack_trader_bot import SlackTraderBot 
from app.analysis.constants import MACD, RSI, OBV, ADX
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

def _fetch_analysis_configs(symbol: str, db: Any, auth_token: str) -> Dict[str, Any]:
    values: Dict[str, Dict[str, Any]] = db.child(f'{symbol}/ANALYSIS').get(auth_token).val()

    return {
        MACD: values[MACD],
        RSI: values[RSI],
        OBV: values[OBV],
        ADX: values[ADX]
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
             web_hook_url: str,
             firebase: Tuple[Any, str],
             time_stock_series_df: DataFrame) -> None:

    slack_trader_bot: SlackTraderBot = SlackTraderBot(symbol, web_hook_url)
    configs: Dict[str, Any] = _fetch_analysis_configs(symbol, *firebase)

    analysis_results: Dict[str, Tuple] = _run_analysis(configs, time_stock_series_df)
    suggestion: str = _interpret_analysis()

    # slack_trader_bot.post(suggestion, analysis_results)

if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv
    from pyrebase.pyrebase import initialize_app, Firebase, Auth
    
    from constants import COFING_SPREAD_SHEET_ID, WEB_HOOK_URL  
    from app.constants import FIREBASE_CONFIG
    from app.analysis.mock_constants import TESLA


    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.TSLA'))
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')
    web_hook_url: str = environ.get(WEB_HOOK_URL, '')

    fb_app: Firebase = initialize_app(FIREBASE_CONFIG)

    fb_auth: Auth = fb_app.auth()
    fb_project_token: bytes = fb_auth.create_custom_token('7b89e2cf-0139-4ce2-95d8-d0f79bdf24fc')
    fb_user: Dict[str, str] = fb_auth.sign_in_with_custom_token(fb_project_token)

    analysis(
        Datetime.now(),
        'TSLA',
        web_hook_url,
        (fb_app.database(), fb_user['idToken']),
        TESLA
    )
