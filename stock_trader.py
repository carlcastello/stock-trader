from os import path, environ
from dotenv import load_dotenv

from typing import Optional, List, Set, Tuple

from app import start_app
from constants import TRADING_SPREAD_SHEET_ID, HISTORICAL_SPREAD_SHEET_ID, COFING_SPREAD_SHEET_ID

def main() -> None:
    dotenv_path = path.join(path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    trading_spread_sheet_id: str = environ.get(TRADING_SPREAD_SHEET_ID, '')
    historical_spread_sheet_id: str = environ.get(HISTORICAL_SPREAD_SHEET_ID, '')
    config_spread_sheet_id: str = environ.get(COFING_SPREAD_SHEET_ID, '')

    if trading_spread_sheet_id and historical_spread_sheet_id and config_spread_sheet_id:
        start_app(config_spread_sheet_id, trading_spread_sheet_id, historical_spread_sheet_id)

if __name__ == '__main__':
    main()