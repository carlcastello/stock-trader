from pandas import DataFrame
from datetime import datetime as DateTime
from multiprocessing import Process, log_to_stderr

from pyrebase.pyrebase import initialize_app, Firebase, Auth
import pyrebase
from alpha_vantage.timeseries import TimeSeries


from typing import Optional, Dict, Any

from app.analysis import analysis
from app.google.google_sheet import GoogleSheet
from app.ticker import Ticker


def start_app(symbol: str, config_spread_sheet_id: str, alpha_vantage_id: str, web_hook_url: str) -> None:
    
    time_series: TimeSeries = TimeSeries(alpha_vantage_id, output_format='pandas')

    firebase: Firebase = initialize_app({
        'apiKey': ' AIzaSyCyFt0bJFjcHEfjWSF3w0_T2Bhri8pjHj4',
        'authDomain': 'thestocktrader-dc81a.firebaseapp.com',
        'databaseURL': 'https://thestocktrader-dc81a.firebaseio.com',
        'storageBucket': 'thestocktrader-dc81a.appspot.com',
        'serviceAccount': 'credentials/firebase_credentials.json'
    })

    authentication: Auth = firebase.auth()
    token: bytes = authentication.create_custom_token('7b89e2cf-0139-4ce2-95d8-d0f79bdf24fc')
    
    print(authentication.sign_in_with_custom_token(token))

    def _ticker_callback(now: DateTime, interval: float) -> None:
        time_stock_series_df, _ = time_series.get_intraday(
            symbol=symbol,
            interval='1min',
            outputsize='compact',
        )

        Process(
            name=str(now),
            target=analysis,
            args=(now, symbol, config_spread_sheet_id, web_hook_url, time_stock_series_df.reset_index(drop=True))
        ).start()

        print(time_stock_series_df)
    ticker: Ticker = Ticker(config_spread_sheet_id, _ticker_callback)
    # ticker.run() 
