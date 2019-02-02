from typing import List

from .google_api import GoogleAPI

class GoogleSheet(GoogleAPI):

    def __init__(self, sheet_id: str) -> None:
        super().__init__('sheets', 'https://www.googleapis.com/auth/spreadsheets')
        
        self._workspace = self._service.spreadsheets()
        self._sheet_id = sheet_id

    def write(self) -> None:
        pass

    def read(self) -> None:
        pass
    
    def create(self) -> None:
        pass