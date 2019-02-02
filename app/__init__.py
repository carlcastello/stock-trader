from typing import Dict, Optional, Any

from app.google.google_sheet import GoogleSheet

def start_app(config: Dict[str, Optional[Any]]) -> None: 
    google_shee: GoogleSheet = GoogleSheet()    

