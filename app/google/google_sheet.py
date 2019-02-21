from typing import List, Any, Optional, Dict

from app.google.google_api import GoogleAPI


class Result:

    def __init__(self, result: List[List[str]]):
        self._row: List[List[str]] = result
        self._column: List[List[str]] = [[row[i] for row in result] for i in range(len(result[0]))]

    def value(self, row_index: int, column_index: int, default: Optional[str] = None) -> str:
        try:
            return self._row[row_index][column_index]
        except IndexError as exception:
            if default:
                return default
            raise Exception('Unexpected behavior reached. Trying to index unknown value.')

    def rows(self) -> List[List[str]]:
        return self._row

    def row(self, index: int) -> List[str]:
        try:
            return self._row[index]
        except IndexError:
            return []

    def column(self, index: int) -> List[Any]:
        try:
            return self._column[index]
        except IndexError:
            return []


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

    def batch_read(self, *ranges: str, **kwargs: str) -> List[Result]:
        results: Dict[str, Any] = self._execute(
            self._worksheet.values().batchGet,
            spreadsheetId=self._spread_sheet_id,
            ranges=list(ranges),
            **kwargs
        )
        return [
            Result(result.get('values', [[]]))
            for result in results.get('valueRanges', [])
        ]
    
    def read(self, range: str, **kwargs: str) -> Result:
        result: Dict[str, Any] =  self._execute(
            self._worksheet.values().get,
            spreadsheetId=self._spread_sheet_id,
            range=range,
            **kwargs
        )

        return Result(result.get('values', [[]]))

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