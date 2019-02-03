from typing import List, Any, Optional, Dict

from .google_api import GoogleAPI

class GoogleSheet(GoogleAPI):

    def __init__(self, sheet_id: str) -> None:
        super().__init__('sheets', 'https://www.googleapis.com/auth/spreadsheets')
        
        self._worksheet = self._service.spreadsheets().values()
        self._sheet_id = sheet_id

    def write(self, range: str, values: List[List[Any]], value_input_option: str = 'USER_ENTERED') -> None:
        self.execute(
            self._worksheet.update,
            spreadsheetId=self._sheet_id,
            range=range,
            valueInputOption=value_input_option,
            body={'values': values}
        )
  
    def read(self, range: str) -> Optional[List[List[Any]]]:
        result: Optional[Dict[str, Any]] =  self.execute(
            self._worksheet.get,
            spreadsheetId=self._sheet_id,
            range=range
        )
        return result.get('values') if result else None

    def create(self) -> None:
        pass