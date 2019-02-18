import logging
from datetime import datetime as DateTime

from typing import Any, Dict, Tuple, Union

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
        def parse_data(key: str, value: Dict[str, str]) -> Tuple[DateTime, float, float, float, float, float]:
            try:
                return \
                    DateTime.strptime(key, '%Y-%m-%d %H:%M:%S'), \
                    float(value.get('1. open', '0')), \
                    float(value.get('2. high', '0')), \
                    float(value.get('3. low', '0')), \
                    float(value.get('4. close', '0')), \
                    float(value.get('5. volume', '0'))
            except ValueError as exception:
                logging.critical('Incompatible data shape.')
                raise exception

        response: Any = super()._get(self.url, fields=self._params)
        if response.get('Error Message'):
            raise Exception(response.get('Error Message'))
        time_series: Dict[str, Dict[str, str]] = response.get(f'Time Series ({self._interval})', {})

        return [
            parse_data(key, value)
            for key, value in time_series.items()
        ]