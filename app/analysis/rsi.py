from pandas import DataFrame
from queue import Queue

def rsi_analysis(queue: Queue, data_frame: DataFrame) -> None:
    queue.put('RSI')