from os import path
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from typing import List

class GoogleSheet:
    def __init__(self, scopes: List[str]) -> None:
        self._authenticate(scopes)
        self._service = build('sheets', 'v4', credentials=self.credentials)

           
    def _authenticate(self, scopes: List[str]) -> None:
        # https://developers.google.com/sheets/api/quickstart/python
        
        if path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
               self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                self.credentials = flow.run_local_server()
            with open('token.pickle', 'wb') as token:
               pickle.dump(self.credentials, token)

    
    def write(self) -> None:
        pass

    def read(self) -> None:
        pass