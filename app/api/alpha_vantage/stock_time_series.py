from datetime import datetime as DateTime

from typing import List, Any, Dict

from app.api import API
from app.analysis.time_series import TimeSeries

class StockTimeSeries(API):

    url: str = 'https://www.alphavantage.co/query'

    def __init__(self, api_key: str, symbol: str, interval: int):
        self._interval = f'{interval}min'

        self._params: Dict[str, str] = {
            'function': 'TIME_SERIES_INTRADAY',
            'outputsize': 'compact',
            'datatype': 'json',
            'symbol': symbol,
            'apikey': api_key,
            'interval': self._interval
        }

    def get(self) -> Any:
        response: Any = super()._get(self.url, fields=self._params)
        if response.get('Error Message'):
            raise Exception('Alpha Vantage: Someting went wrong')
        time_series: Dict[str, Dict[str, str]] = response.get(f'Time Series ({self._interval})', {})

        return [
            TimeSeries(timestamp=key,
                       open=value.get('1. open', '0'),
                       high=value.get('2. high', '0'),
                       low=value.get('3. low', '0'),
                       close=value.get('4. close', '0'),
                       volume=value.get('5. volume', '0'))
            for key, value in time_series.items()
        ]