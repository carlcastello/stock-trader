from app.slack.slack_api import SlackAPI

from typing import Dict, Any, List, Optional

from app.analysis.constants import ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL, POSITION, OBV

class StockTraderBot(SlackAPI):

    _color: str = '#439FE0'

    _footer_name: str = 'StockTraderBot'
    _footer_icon: str = 'https://platform.slack-edge.com/img/default_application_icon.png'

    _order: List[str] = [ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL, POSITION, OBV]

    _boolead_analysis: List[str] = [OBV]
    _boolean_fields: List[str] = ['Current']

    _qualitative_analysis: List[str] = [POSITION]
    _qualitative_fields: List[str] = ['Current', 'Previous']

    _quantitative_analysis: List[str] = [ADX, POS_DI, NEG_DI, RSI, MACD, SIGNAL]
    _quantitative_fields: List[str] = ['Current', 'Previous', 'Minimum', 'Maximum', 'Mean', 'Slope']

    def __init__(self, symbol: str, url: str):
        super().__init__(url)
        self._symbol: str = symbol

    def _build_payload(self, key: str, field_keys: List[str], result: Any) -> Dict[str, Any]: 
        fallback: str = f'{key}:'
        fields: List[Dict[str, Any]] = []

        for index in range(len(field_keys)):
            curr_field: str = field_keys[index]
            curr_value: float = result[index]

            fallback += f' {curr_field}(`{curr_value}`)'
            fields.append({ 'title': curr_field, 'value': f'`{curr_value}`', 'short': True })

        fallback += '\n'
        
        return {
            'title': key,
            'fallback': fallback,
            'fields': fields,
            'color': self._color,
            'footer': self._footer_name,
            'footer_icon': self._footer_icon,
            'ts': '123456789'
        }


    def post(self, suggestion: str, results: Dict[str, Any]) -> None:
        attatchments: List[Dict[str, Any]] = []
        
        for key in self._order:
            result: Optional[Any] = results.get(key)

            fields: List[str] = []
        
            if key in self._qualitative_analysis:
                fields = self._qualitative_fields
            elif key in self._quantitative_analysis:
                fields = self._quantitative_fields
            elif key in self._boolead_analysis:
                fields = self._boolean_fields

            if result and fields:
                attatchments.append(self._build_payload(key, fields, result))


        self._post({
            'text': f'*Symbol*: `{self._symbol}` \n *Suggestion*: `{suggestion}` \n <!channel|channel>',
            'attachments': attatchments
        })


if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv

    from constants import WEB_HOOK_URL  

    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    web_hook_url: str = environ.get(WEB_HOOK_URL, '')
    stock_trader_bot: StockTraderBot = StockTraderBot('TESLA', web_hook_url)

    results: Dict[str, Any] = {
        RSI: (38.89207954405839, 39.32179006735938, 36.384792388365135, 39.32179006735938, 37.99562454646287, 0.3855717821057254, [37.87077060188745, 37.50869013064398, 36.384792388365135, 39.32179006735938, 38.89207954405839])
    }

    stock_trader_bot.post('BUY', results)