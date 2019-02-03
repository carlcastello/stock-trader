import pickle
import logging
from os import path


from typing import List, Any, Callable

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleAPI:

    def __init__(self, service_name: str, scope: str):
        # https://developers.google.com/sheets/api/quickstart/python
        
        credentials: Credentials = None

        if path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
               credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/google_credentials.json',
                    scope
                )
                credentials = flow.run_local_server()
            with open('credentials/token.pickle', 'wb') as token:
               pickle.dump(credentials, token)

        self.service_name: str = service_name
        self._service: Resource = build(self.service_name, 'v4', credentials=credentials) 

    def execute(self, callable: Callable[..., Any], **kwargs) -> Any:
        try:
            return callable(**kwargs).execute()
        except HttpError as error:
            logging.critical(f'Unexpected response for `{self.service_name.upper()}`: {error}')
        return {}