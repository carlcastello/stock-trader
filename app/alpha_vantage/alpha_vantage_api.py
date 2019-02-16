class AlphaVantageAPI:

    url: str = 'https://www.alphavantage.co/'

    def __init__(self, api_id: str):
        self.api_id = api_id

    