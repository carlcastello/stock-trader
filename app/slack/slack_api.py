from json import dumps
from requests import post, ConnectionError, Timeout, HTTPError

from typing import Dict, Any

class SlackAPI:

    def __init__(self, url: str) -> None:
        self._url: str = url

    def _post(self, data: Dict[str, Any]) -> None:
        try:
            response = post(url=self._url, data=dumps(data))
            print(response.text) 
        except HTTPError as error:
            raise error
        except ConnectionError:
            raise error
        except Timeout:
            raise error
   
    def _get(self) -> None:
        raise NotImplementedError()

if __name__ == "__main__":
    from os import path, environ
    from dotenv import load_dotenv

    from constants import WEB_HOOK_URL  

    file_path: str = path.dirname(__file__)
    load_dotenv(path.join(file_path, '../../env/.COMMON'))

    web_hook_url: str = environ.get(WEB_HOOK_URL, '')
    slack_api: SlackAPI = SlackAPI(web_hook_url)
    slack_api._post({"text": "Hello, World! Love, Python."})