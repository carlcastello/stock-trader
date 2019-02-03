from typing import Dict, Optional, Any

from constants import GOOGLE_SPREAD_SHEET_ID
from app.google.google_sheet import GoogleSheet

def start_app(config: Dict[str, Optional[Any]]) -> None: 
    pass
#     spread_sheet_id: Optional[str] = config.get(GOOGLE_SPREAD_SHEET_ID)
#     if spread_sheet_id:
#         google_sheet: GoogleSheet = GoogleSheet(spread_sheet_id)
#         google_sheet.write('Config!A2', [['CARL']])
#         google_sheet.read('A1')
#         google_sheet.create_sheet('Hello')