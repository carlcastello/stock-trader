from typing import List

from .google_api import GoogleAPI

class GoogleSheet(GoogleAPI):

    def __init__(self, scope: str) -> None:
        super().__init__('sheets', scope)
        self._sheet = self._service.spreadsheets()
    
    def write(self) -> None:
        pass

    def read(self) -> None:
        pass