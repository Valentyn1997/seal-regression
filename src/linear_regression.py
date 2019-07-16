from src.encarray import EncArray
from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecryptorUtils
import numpy as np
from seal import Plaintext


class SecureLinearRegression:
    def __init__(self):
        """
        Linear regression, working with encrypted arrays of fractional numbers.

        Examples:
        >> from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecryptorUtils
        >> context = FracContext()
        >> encode_utils = FractionalEncoderUtils(context)
        >> decode_utils = FractionalDecryptorUtils(context)
        >>
        >> X = [[1.0, 1.0],
        >>      [1.0, 2.0],
        >>      [1.0, -1.0],
        >>      [1.0, 2.0]]
        >> y = [[2.0], [-1.0], [2.0], [4.0]]
        >>
        >> X_enc = EncArray(X, enc_utils=encode_utils)
        >> y_enc = EncArray(y, enc_utils=encode_utils)
        >>
        >> model = SecureLinearRegression()
        >> model.fit_unencrypted(X, y, n_iter=20)
        >> print(f'Estimated result (unencrypted): {model.weigths}')
        >>
        >> model.fit(X_enc, y_enc, n_iter=20, verbose=True, decode_utils=decode_utils)
        >> print(f'Estimated result (encrypted): {model.weigths.decrypt_array(decode_utils)}')
        >>
        >> print(f'Prediction (encrypted): {model.predict(X_enc).decrypt_array(decode_utils)}. '
        >>       f'Real values: {y_enc.decrypt_array(decode_utils)}')

        """
        self.weigths = None
        self.coef = None

    def fit_unencrypted(self, X, y, lr=0.2, n_iter=10, verbose=False):
        """
        Gradient-descent based least-squares parameter estimation for unencrypted data (for comparison).
        :param X: unencrypted design matrix
        :param y: unencrypted target variable
        :param lr: learning rate
        :param n_iter: number of iterations
        """
        X = np.array(X)
        y = np.array(y)

        self.weigths = np.array(X.shape[1] * [0.0])
        self.coef = np.array(X.shape[1] * [lr / X.shape[0]])

        for it in (range(n_iter)):
            gradient = []
            for j in range(X.shape[1]):
                loss = []
                for i in range(X.shape[0]):
                    loss.append(((self.weigths * X[i]).sum() - y[i][0]))
                loss = np.array(loss)
                gradient.append((loss * X.T[j]).sum())
            gradient = np.array(gradient)
            if verbose:
                print(f'Iteration: {it}. Gradient: {gradient}')

            self.weigths = self.weigths - self.coef * gradient
        # print(f'Real result: {(np.linalg.inv(X.T@X) @X.T @ y).T[0]}')

    def fit(self, X: EncArray, y: EncArray, decode_utils: FractionalDecryptorUtils = None, init_weights: EncArray = None,
            lr=0.2, n_iter=10, verbose=False):
        """
        Gradient-descent based least-squares parameter estimation for encrypted data.
        :param X: encrypted design matrix
        :param y: encrypted target variable
        :param decode_utils: decoder utils for monitoring
        :param init_weights: encrypted initial value for weights
        :param lr: learning rate
        :param n_iter: number of iterations
        :param verbose: if True, noise budget and size is printed after each iteration
        """
        # Ininitializing weights
        if init_weights is None:
            self.weigths = EncArray(X.shape[1] * [0.0], enc_utils=X.enc_utils)
        else:
            self.weigths = init_weights

        # Learning weight divided by sample size
        if type(self.coef) != EncArray:
            self.coef = EncArray(X.shape[1] * [lr / X.shape[0]], enc_utils=X.enc_utils, dtype=Plaintext)

        # Gradient descent
        for it in (range(n_iter)):
            gradient = []
            for j in range(X.shape[1]):
                loss = []
                for i in range(X.shape[0]):
                    loss.append(((self.weigths * X[i]).sum() - y[i][0]).enc_arr)
                loss = EncArray(loss, enc_utils=X.enc_utils)
                gradient.append((loss * X.T[j]).sum().enc_arr)
            gradient = EncArray(gradient, enc_utils=X.enc_utils)
            if verbose:
                print(f'Iteration: {it}. Gradient: {gradient.decrypt_array(decode_utils)}. '
                      f'Noise budget: {self.weigths.noise_budget(decode_utils)}. '
                      f'Size of weights: {self.weigths.mem_size()}')
            else:
                print(f'Iteration: {it}')
            self.weigths = self.weigths - self.coef * gradient

    def predict(self, X: EncArray) -> EncArray:
        """
        Prediction for data X.
        :param X: encrypted design matrix
        :return: predicted target
        """
        weights_extended = EncArray([self.weigths.enc_arr], X.enc_utils)
        return X @ weights_extended
