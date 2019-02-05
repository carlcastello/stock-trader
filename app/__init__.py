import logging
from pytz import timezone
from datetime import datetime

from typing import Dict, Optional, Any, List

from constants import GOOGLE_SPREAD_SHEET_ID
from app.google.google_sheet import GoogleSheet

TIME_ZONE: str = ''


def get_time_zone(google_sheet: GoogleSheet) -> None:
    global TIME_ZONE
    
    if not TIME_ZONE:
        value: Optional[List[List[str]]] = google_sheet.read('Config!B2')
        if value and value[0]:
            TIME_ZONE = value[0][0]
        else:
            logging.critical('Could not find TIME_ZONE. Program terminated.')
            

def start_app(trade_spread_sheet_id: str) -> None: 
    trade_sheet: GoogleSheet = GoogleSheet(trade_spread_sheet_id)
    get_time_zone(trade_sheet)

    date: str = datetime.now(timezone(TIME_ZONE)).strftime('%Y-%m-%d')
    trade_sheet.create_sheet(date)

    #  google_sheet: GoogleSheet = GoogleSheet(spread_sheet_id)

    # print(datetime.now(timezone('Canada/Eastern')).weekday())
    # trade_spread_sheet_id: Optional[str] = config.get(GOOGLE_SPREAD_SHEET_ID)
    # if trade_spread_sheet_id:
    #     google_sheet: GoogleSheet = GoogleSheet(trade_spread_sheet_id)

    #     if not time_zone:
    #         time_zone = 

#         google_sheet.write('Config!A2', [['CARL']])
#         google_sheet.read('A1')2
#         google_sheet.create_sheet('Hello')