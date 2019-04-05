from pandas import DataFrame
from datetime import datetime as DateTime
from alpha_vantage.timeseries import TimeSeries
from pyrebase.pyrebase import initialize_app, Auth, Firebase, Database

from typing import Optional, Dict, Any, Tuple

from app.analysis import analysis
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker

def start_app(symbol: str, project_id: str, alpha_vantage_id: str, web_hook_url: str, firbase_config: Dict[str, str]) -> None:
    time_series: TimeSeries = TimeSeries(alpha_vantage_id, output_format='pandas')

    fb_app: Firebase = initialize_app(firbase_config)

    fb_auth: Auth = fb_app.auth()
    fb_project_token: bytes = fb_auth.create_custom_token(project_id)
    fb_user: Dict[str, str] = fb_auth.sign_in_with_custom_token(fb_project_token)
    fb_db: Database = fb_app.database()

    def _ticker_callback(now: DateTime, auth_token: str) -> None:
        time_stock_series_df, _ = time_series.get_intraday(
            symbol=symbol,
            interval='1min',
            outputsize='compact',
        )
 
        firebase: Tuple[Auth, str] = (fb_db, auth_token)
        analysis(now, symbol, web_hook_url, firebase, time_stock_series_df.reset_index(drop=True))

    firebase: Tuple[Auth, Any, str, str] = (fb_auth, fb_db, fb_user['idToken'], fb_user['refreshToken'])

    ticker: Ticker = Ticker(symbol, firebase, _ticker_callback)
    ticker.run()
