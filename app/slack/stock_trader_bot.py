from app.slack.slack_api import SlackAPI

from typing import Dict, Any, List, Optional

from app.analysis.constants import ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL, POSITION, OBV

class StockTraderBot(SlackAPI):

    _order: List[str] = [ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL, POSITION, OBV]
    _quantitative_feilds: List[str] = ['Curr', 'Prev', 'Min', 'Max', 'Mean', 'Slope']

    def __init__(self, url: str):
        super().__init__(url)
    
    def post(self, suggestion: str, results: Dict[str, Any]) -> None:
        attatchments: List[Dict[str, Any]] = []
        for key in self._order:
            result: Optional[Any] = results.get(key)
            if result and len(result) == len(self._quantitative_feilds) + 1:
                fallback: str = f'{key}:'
                fields: List[Dict[str, Any]] = []

                for index in range(len(self._quantitative_feilds)):
                    curr_field: str = self._quantitative_feilds[index]
                    curr_value: float = result[index]

                    fallback += f' {curr_field}(`{curr_value}`)'
                    fields.append({ 'title': curr_field, 'value': f'`{curr_value}`', 'short': True })

                fallback += '\n'

                attatchments.append({
                    'title': key,
                    'fallback': fallback,
                    'fields': fields
                })

        self._post({
            'text': f'*Suggestion*: `{suggestion}`',
            'attachments': attatchments
        })


if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv

    from constants import WEB_HOOK_URL  

    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    web_hook_url: str = environ.get(WEB_HOOK_URL, '')
    stock_trader_bot: StockTraderBot = StockTraderBot(web_hook_url)

    results: Dict[str, Any] = {
        RSI: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
    }

    stock_trader_bot.post('BUY', results)