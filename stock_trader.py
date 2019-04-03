from argparse import ArgumentParser
from os import path, environ
from dotenv import load_dotenv
from multiprocessing import Process

from typing import Optional, List, Set, Tuple, Dict

from app import start_app
from constants import SYMBOL, COFING_SPREAD_SHEET_ID, ALPHA_VANTAGE_ID, WEB_HOOK_URL, FB_API_KEY, \
        FB_AUTH_DOMAIN, FB_DB_URL, FB_SERVICE_ACCOUNT, FB_STORAGE_BUCKET

def main() -> None:
    parser: ArgumentParser = ArgumentParser(description='Stock Trader program.')
    parser.add_argument('symbol', type=str, help='The stock symbol.')

    file_path: str = path.dirname(__file__)
    dotenv_path = path.join(path.dirname(__file__), f'env/.{parser.parse_args().symbol}')
    
    load_dotenv(path.join(file_path, f'env/.{parser.parse_args().symbol}'))
    load_dotenv(path.join(file_path, f'env/.COMMON'))

    alpha_vantage_id: Optional[str] = environ.get(ALPHA_VANTAGE_ID)
    symbol: Optional[str] = environ.get(SYMBOL)
    web_hook_url: Optional[str] = environ.get(WEB_HOOK_URL)

    fb_api_key: Optional[str] = environ.get(FB_API_KEY)
    fb_auth_domain: Optional[str] = environ.get(FB_AUTH_DOMAIN)
    fb_db_url: Optional[str] = environ.get(FB_DB_URL)
    fb_service_account: Optional[str] = environ.get(FB_SERVICE_ACCOUNT)
    fb_storage_bucket: Optional[str] = environ.get(FB_STORAGE_BUCKET)

    if symbol and alpha_vantage_id and web_hook_url and \
        fb_api_key and fb_auth_domain and fb_db_url and fb_service_account and fb_storage_bucket:

        firebase_config: Dict[str, str] = {
            'apiKey': fb_api_key,
            'authDomain': fb_auth_domain,
            'databaseURL': fb_db_url,
            'storageBucket': fb_storage_bucket,
            'serviceAccount': fb_service_account
        }

        process: Process = Process(
            name=str(symbol),
            target=start_app,
            args=(symbol, alpha_vantage_id, web_hook_url, firebase_config)
        )
        process.start()

        print(f'Running Process {process.pid}...')

if __name__ == '__main__':
    main()