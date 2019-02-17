from json import loads
import certifi
from urllib3 import PoolManager
from urllib3.exceptions import RequestError, HTTPError
from urllib.parse import urlencode

from typing import Dict, Any

class API:

    _http: PoolManager = PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )

    def __init__(self) -> None:
        pass
    
    def __request(self,
                  method: str,
                  url: str,
                  fields: Dict[str, Any] = None,
                  headers: Dict[str, Any] = None) -> Any:
        try:
            response: Any = loads(self._http.request(
                method,
                url,
                headers=headers,
                fields=fields
            ).data.decode('utf-8'))
        except Exception as error:
            print(error)
            raise error
        else:
            return response

    def _get(self,
            url: str, 
            fields: Dict[str, Any] = None,
            headers: Dict[str, Any] = None) -> Any:

        return self.__request('GET', url, headers=headers, fields=fields)