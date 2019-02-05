from sched import scheduler as Scheduler

from app.google.google_sheet import GoogleSheet

class Trader:

    def __init__(self,
                 scheduler: Scheduler,
                 trade_sheet: GoogleSheet,
                 historical_sheet: GoogleSheet,
                 *arg: str):
        pass

    def start(self) -> None:
        pass
