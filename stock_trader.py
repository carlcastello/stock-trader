from argparse import ArgumentParser
from os import path, environ
from dotenv import load_dotenv

from typing import Optional, List, Set, Tuple

from app import start_app
from constants import SYMBOL, COFING_SPREAD_SHEET_ID, ALPHA_VANTAGE_ID, WEB_HOOK_URL

def main() -> None:
    parser: ArgumentParser = ArgumentParser(description='Stock Trader program.')
    parser.add_argument('symbol', type=str, help='The stock symbol.')

    file_path: str = path.dirname(__file__)
    dotenv_path = path.join(path.dirname(__file__), f'env/.{parser.parse_args().symbol}')
    
    load_dotenv(path.join(file_path, f'env/.{parser.parse_args().symbol}'))
    load_dotenv(path.join(file_path, f'env/.COMMON'))

    alpha_vantage_id: Optional[str] = environ.get(ALPHA_VANTAGE_ID)
    config_spread_sheet_id: Optional[str] = environ.get(COFING_SPREAD_SHEET_ID)
    symbol: Optional[str] = environ.get(SYMBOL)
    web_hook_url: Optional[str] = environ.get(WEB_HOOK_URL)

    if symbol and config_spread_sheet_id and alpha_vantage_id and web_hook_url:
        start_app(symbol, config_spread_sheet_id, alpha_vantage_id, web_hook_url)

if __name__ == '__main__':
    main()