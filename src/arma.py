from src.encarray import EncArray
from src.fractions_utils import FracContext, FractionalEncoderUtils, FractionalDecoderUtils
from typing import Tuple

class ARMA:
    def __init__(self):
        pass

    def fit(self, ts: EncArray, lag):
        X, y = self.create_design_matrix(ts, lag)
        noise_estimator = Linear_Regression()

    @staticmethod
    def create_design_matrix(ts: EncArray, lag) -> Tuple[EncArray, EncArray]:
        X = []
        intercept = EncArray((len(ts) - lag)*[1], enc_utils=ts.enc_utils).enc_arr
        X.append(intercept)
        for shift in range(1, lag+1):
            X.append(ts.T[0].enc_arr[lag-shift:len(ts) - shift])
        return EncArray(X, enc_utils=ts.enc_utils).T, ts[lag:]