from pandas import DataFrame
from datetime import datetime as DateTime
from multiprocessing import Process
from alpha_vantage.timeseries import TimeSeries
from pyrebase.pyrebase import initialize_app, Auth, Firebase

from typing import Optional, Dict, Any, Tuple

from app.analysis import analysis
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker

def start_app(symbol: str, alpha_vantage_id: str, web_hook_url: str, firbase_config: Dict[str, str]) -> None:
    time_series: TimeSeries = TimeSeries(alpha_vantage_id, output_format='pandas')

    fb_app: Firebase = initialize_app(firbase_config)

    fb_auth: Auth = fb_app.auth()
    fb_project_token: bytes = fb_auth.create_custom_token('7b89e2cf-0139-4ce2-95d8-d0f79bdf24fc')
    fb_user: Dict[str, str] = fb_auth.sign_in_with_custom_token(fb_project_token)
    
    def _ticker_callback(now: DateTime, auth_token: str) -> None:
        time_stock_series_df, _ = time_series.get_intraday(
            symbol=symbol,
            interval='1min',
            outputsize='compact',
        )
 
        firebase: Tuple[Auth, str] = (fb_app.database(), auth_token)
        Process(
            name=str(now),
            target=analysis,
            args=(now, symbol, web_hook_url, firebase, time_stock_series_df.reset_index(drop=True))
        ).start()

    firebase: Tuple[Auth, Any, str, str] = (fb_auth, fb_app.database(), fb_user['idToken'], fb_user['refreshToken'])

    ticker: Ticker = Ticker(symbol, firebase, _ticker_callback)
    ticker.run() 
