from os import path, environ
from dotenv import load_dotenv

from typing import Optional, List, Set, Tuple

from app import start_app
from constants import ENV_CONSTANTS

def main() -> None:
    dotenv_path = path.join(path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    start_app({ constant: environ.get(constant) for constant in ENV_CONSTANTS })

if __name__ == "__main__":
    main()