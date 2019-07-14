from src.encarray import EncArray

class ARMA:
    def __init__(self):
        pass

    def fit(self, ts: EncArray, lag):
        X = self._create_design_matrix(ts, lag)

    def _create_design_matrix(self, ts, lag):
        pass

