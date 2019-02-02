from os import path
import pickle

from typing import List

from googleapiclient.discovery import build, Resource
from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleAPI:

    def __init__(self, service_name: str, scope: str):
        # https://developers.google.com/sheets/api/quickstart/python
        
        credentials: Credentials = None

        if path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
               credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file('credentials.json', scope)
                credentials = flow.run_local_server()
            with open('token.pickle', 'wb') as token:
               pickle.dump(credentials, token)

        self._service: Resource = build(service_name, 'v4', credentials=credentials) 

