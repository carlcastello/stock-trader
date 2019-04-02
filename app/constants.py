from typing import Dict

FIREBASE_CONFIG: Dict[str, str] = {
    'apiKey': ' AIzaSyCyFt0bJFjcHEfjWSF3w0_T2Bhri8pjHj4',
    'authDomain': 'thestocktrader-dc81a.firebaseapp.com',
    'databaseURL': 'https://thestocktrader-dc81a.firebaseio.com',
    'storageBucket': 'thestocktrader-dc81a.appspot.com',
    'serviceAccount': 'credentials/firebase_credentials.json'
}

# Firebase DB key
TICKER: str = 'TICKER'
TIMEZONE: str = 'TIMEZONE'
INTERVAL: str = 'INTERVAL'
OPENING_HOURS: str = 'OPENING_HOURS'
CLOSING_HOURS: str = 'CLOSING_HOURS'
SHOULD_TRADE: str = 'SHOULD_TRADE'