from queue import Queue
from numpy import nan
from pandas import DataFrame

from typing import Dict, Any, Tuple, List, Optional

from app.analysis.constants import ADX, DX, NEG_DI, POS_DI, NEG_DM_AVG, POS_DM_AVG, TR_AVG, NEG_DM, POS_DM, TR, PERIODS, SPAN
from app.analysis.technical_analysis import TechnicalAnalysis, ParametersNotCompleteException

class AdxAnalysis(TechnicalAnalysis):
    
    _diff_columns: List[str] = [TR, POS_DM, NEG_DM]
    _dm_avg_columns: List[str] = [TR_AVG, POS_DM_AVG, NEG_DM_AVG]
    _dx_columns: List[str] = [POS_DI, NEG_DI, DX]

    def __init__(self, queue: Queue, periods: int, span: int, config: Dict[str, Any], data_frame: DataFrame):

        data_frame[TR] = 0
        data_frame[POS_DM] = 0
        data_frame[NEG_DM] = 0
        data_frame[TR_AVG] = 0
        data_frame[POS_DM_AVG] = 0
        data_frame[NEG_DM_AVG] = 0
        data_frame[POS_DI] = 0
        data_frame[NEG_DI] = 0
        data_frame[DX] = 0
        data_frame[ADX] = 0

        super().__init__(config, data_frame)
        
        self._span: int = span

        self._periods: int = periods
        self._previous_periods: int = periods - 1

        self._adx_period_start: int = periods * 2

    def _calculate_smoothed_average(self, current_value: float, previous_average: float) -> float:
        return (previous_average - (previous_average / self._periods) + current_value)

    @staticmethod
    def _calculate_dx(tr_avg: float, pos_dm_avg: float, neg_dm_avg: float) -> Tuple[float, float, float]:
        pos_di: float = (pos_dm_avg / tr_avg) * 100
        neg_di: float = (neg_dm_avg / tr_avg) * 100
        di_sum: float = pos_di + neg_di
        di_diff: float = abs(pos_di - neg_di)

        return pos_di, neg_di, (di_diff / di_sum) * 100

    @staticmethod
    def _calculate_dm(high: float, low: float, prev_high: float, prev_low: float, prev_close: float) -> Tuple[float, float, float]:
        pos_dm = high - prev_high
        neg_dm = prev_low - low

        if pos_dm > neg_dm:
            neg_dm = 0
        else:
            pos_dm = 0

        return max([high - low, abs(high - prev_close), abs(low - prev_close)]), pos_dm, neg_dm

    def _calculate_dm_average(self, index: int, tr: float, pos_dm: float, neg_dm: float,
                              prev_tr_avg: float, prev_pos_dm_avg: float, prev_neg_dm_avg: float) -> Tuple[float, float, float]:
        tr_avg: float = 0.0
        pos_dm_avg: float = 0.0
        neg_dm_avg: float = 0.0

        if index == self._periods:
            tr_avg, pos_dm_avg, neg_dm_avg = self._data_frame.loc[:self._previous_periods, self._diff_columns].sum()
        else:
            tr_avg = self._calculate_smoothed_average(tr, prev_tr_avg)
            pos_dm_avg = self._calculate_smoothed_average(pos_dm, prev_pos_dm_avg)
            neg_dm_avg = self._calculate_smoothed_average(neg_dm, prev_neg_dm_avg)

        return tr_avg, pos_dm_avg, neg_dm_avg

    def _calculate_adx(self, index: int, dx: float, prev_adx: float) -> float:
        if index == self._adx_period_start:
            return self._data_frame.loc[self._periods: self._adx_period_start, DX].mean()
        else:
            return (dx + (prev_adx * self._previous_periods)) / self._periods

    def run_analysis(self) -> None:

        for index, (_, high, low, close, _, tr, pos_dm, neg_dm, tr_avg, pos_dm_avg, neg_dm_avg, _, _, _, _) in self._data_frame[1:].iterrows():
            _, prev_high, prev_low, prev_close, _, prev_tr, _, _, prev_tr_avg, prev_pos_dm_avg, prev_neg_dm_avg, _, _, _, prev_adx = \
                 self._data_frame.iloc[index - 1]

            tr, pos_dm, neg_dm = self._calculate_dm(high, low, prev_high, prev_low, prev_close)
            self._data_frame.loc[index, self._diff_columns] = tr, pos_dm, neg_dm

            if index >= self._periods:
                tr_avg, pos_dm_avg, neg_dm_avg = self._calculate_dm_average(
                    index, tr, pos_dm, neg_dm,
                    prev_tr_avg, prev_pos_dm_avg, prev_neg_dm_avg
                )
                self._data_frame.loc[index, self._dm_avg_columns] = tr_avg, pos_dm_avg, neg_dm_avg
                pos_di, neg_di, dx = self._calculate_dx(tr_avg, pos_dm_avg, neg_dm_avg)
                self._data_frame.loc[index, self._dx_columns] = pos_di, neg_di, dx

                if index >= self._adx_period_start:
                    self._data_frame.loc[index, ADX] = self._calculate_adx(index, dx, prev_adx) 

    def return_values(self) -> Dict[str, Tuple[float, float, float, float, float, float, float, List[float]]]:
        adx: DataFrame = self._data_frame.tail(self._span)[ADX]
        pos_di: DataFrame = self._data_frame.tail(self._span)[POS_DI]
        neg_di: DataFrame = self._data_frame.tail(self._span)[NEG_DI]

        return {
            ADX: self._return_quantative_values(self._span, adx),
            POS_DI: self._return_quantative_values(self._span, pos_di),
            NEG_DI: self._return_quantative_values(self._span, neg_di)
        }

def adx_analyis(queue: Queue, config: Dict[str, Any], data_frame: DataFrame) -> None:
    periods: Optional[int] = config.get(PERIODS)
    span: Optional[int] = config.get(SPAN)

    if periods and span:
        adx: AdxAnalysis = AdxAnalysis(queue, periods, span, config, data_frame.copy())
        adx.run_analysis()
        queue.put(adx.return_values())
    else:
        raise ParametersNotCompleteException('ADX: Lacks appropriate settings to run ADX analysis')

if __name__ == "__main__":
    from app.analysis.mock_constants import TESLA

    queue: Queue = Queue()
    adx_analyis(queue, {PERIODS: 7, SPAN: 7}, TESLA)
    print(queue.get())


