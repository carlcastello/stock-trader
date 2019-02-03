from typing import Dict, Optional, Any

from constants import GOOGLE_SPREAD_SHEET_ID
from app.google.google_sheet import GoogleSheet

def start_app(config: Dict[str, Optional[Any]]) -> None: 
    sheet_id: Optional[str] = config.get(GOOGLE_SPREAD_SHEET_ID)
    if sheet_id:
        google_sheet: GoogleSheet = GoogleSheet('sheet_id')
        google_sheet.write('A1', [['CARL']])
        google_sheet.read('A1')