from os import path, environ
from dotenv import load_dotenv

from typing import Optional, List, Set, Tuple

from app import start_app
from constants import GOOGLE_SPREAD_SHEET_ID

def main() -> None:
    dotenv_path = path.join(path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    trade_spread_sheet_id: str = environ.get(GOOGLE_SPREAD_SHEET_ID, '')

    if trade_spread_sheet_id:
        start_app(trade_spread_sheet_id)

if __name__ == '__main__':
    main()