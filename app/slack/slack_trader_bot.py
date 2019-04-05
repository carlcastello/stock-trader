from datetime import datetime as Datetime
from app.slack.slack_api import SlackAPI

from typing import Dict, Any, List, Optional, Union, Tuple

from app.analysis.constants import ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL, POSITION, OBV

class SlackTraderBot(SlackAPI):

    _color: str = '#439FE0'

    _footer_name: str = 'StockTraderBot'
    _footer_icon: str = 'https://platform.slack-edge.com/img/default_application_icon.png'

    _quantitative_fields: List[str] = ['Current', 'Previous', 'Minimum', 'Maximum', 'Mean', 'Median', 'Slope']

    def __init__(self, symbol: str, url: str):
        super().__init__(url)
        self._symbol: str = symbol

    _analysis_types: List[str] = [OBV, MACD, ADX, RSI]
    _displayable_analysis_types: Dict[str, List[str]] = {
        MACD: [MACD],
        OBV: [OBV],
        ADX: [ADX],
        RSI: [RSI]
    }

    def _create_attachments(self, now: Datetime, title: str, result: Tuple) -> Dict[str, Union[str, List[Dict[str, Any]], float]]:
        return {
            'title': title,
            'fields': [
                {'title': self._quantitative_fields[index], 'value': result[index], 'short': True }
                for index in range(len(self._quantitative_fields))
            ],
            'color': self._color,
            'footer': self._footer_name,
            'footer_icon': self._footer_icon,
            'ts': now.timestamp()
        }

    def post(self, now: Datetime, messages: List[str], results: Dict[str, Dict[str, Tuple]]) -> None:
        attachments: List[Dict[str, Any]] = []

        for analysis_type in self._analysis_types:
            displayable_types: List[str] = self._displayable_analysis_types[analysis_type]
            for key, value in results[analysis_type].items():
                if key in displayable_types:
                    attachments.append(self._create_attachments(now, key, value))


        message: str = '\n'.join(messages)
        self._post({
            'text': f'<!channel|channel> \n *Date*: {now.strftime("%Y-%d-%m %H:%M:%S")} \n *Message*: ```{message}```',
            'attachments': attachments
        })


if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv

    from constants import WEB_HOOK_URL  

    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    web_hook_url: str = environ.get(WEB_HOOK_URL, '')
    stock_trader_bot: SlackTraderBot = SlackTraderBot('TESLA', web_hook_url)

    results: Dict[str, Any] = {
        MACD: {
            MACD: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
        },
        ADX: {
            ADX: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
        },
        OBV: {
            OBV: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
        },
        RSI: {
            RSI: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
        }
    }

    stock_trader_bot.post(Datetime.now(), [MACD, ADX, RSI, OBV], results)