from typing import List, Any, Optional, Dict

from .google_api import GoogleAPI

# class ValueRange: 
    
#     def __init__(self, range: str, major_dimension: str = 'ROWS', **kwargs : str):
#         self._range = range
#         self._major_dimension = major_dimension
#         self._kwargs = kwargs
    
#     def to_google_json(self) -> Dict[str, Any]:
#         return {
#             'range': self._range,
#             'majorDimension': self._major_dimension,
#             **self._kwargs,
#         }

class GoogleSheet(GoogleAPI):

    def __init__(self, spread_sheet_id: str) -> None:
        super().__init__('sheets', 'https://www.googleapis.com/auth/spreadsheets')
        
        self._worksheet = self._service.spreadsheets()
        self._spread_sheet_id: str = spread_sheet_id

    def write(self, range: str, values: List[List[Any]], value_input_option: str = 'USER_ENTERED') -> None:
        self._execute(
            self._worksheet.values().update,
            spreadsheetId=self._spread_sheet_id,
            range=range,
            valueInputOption=value_input_option,
            body={'values': values},
        )

    def batch_read(self, ranges: List[str], major_dimension: str = 'ROWS', **kwargs: str) -> Optional[List[List[List[Any]]]]:
        results: Optional[Dict[str, Any]] = self._execute(
            self._worksheet.values().batchGet,
            spreadsheetId=self._spread_sheet_id,
            ranges=ranges,
            majorDimension=major_dimension,
            **kwargs
        )

        if results:
            return [
                result.get('values')
                for result in results.get('valueRanges', []) if result.get('values')
            ]
        
        return None

    def read(self, range: str, major_dimension: str = 'ROWS', **kwargs: str) -> Optional[List[List[Any]]]:
        result: Optional[Dict[str, Any]] =  self._execute(
            self._worksheet.values().get,
            spreadsheetId=self._spread_sheet_id,
            range=range,
            majorDimension=major_dimension,
            **kwargs
        )
        return result.get('values') if result else None

    def create_sheet(self, title: str) -> None:
        self._execute(
            self._worksheet.batchUpdate,
            spreadsheetId=self._spread_sheet_id,
            body={
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'columnCount': 2
                            }
                        }
                    }
                }]
            }
        )