from src.fractions_utils import Fractionals_utils


class Linear_Regression:
    def __init__(self, weights=None):
        self.utils = Fractionals_utils()
        if not weights == None:
            self.weights = weights
        else:
            pass

    def fit(self, x, y):
        pass

    def predict(self, x):
        pass
