from os import path, environ
from dotenv import load_dotenv

from typing import Optional, List, Set, Tuple

from app import start_app
from constants import SYMBOL, COFING_SPREAD_SHEET_ID, ALPHA_VANTAGE_ID

def main() -> None:
    dotenv_path = path.join(path.dirname(__file__), 'env/.tesla')
    load_dotenv(dotenv_path)

    alpha_vantage_id: str = environ.get(ALPHA_VANTAGE_ID, '')
    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')
    symbol: str = environ.get(SYMBOL, '')

    if symbol and config_spread_sheet_id and alpha_vantage_id:
        start_app(symbol, config_spread_sheet_id, alpha_vantage_id)

if __name__ == '__main__':
    main()