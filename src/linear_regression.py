from src.arma import ARMA
from src.encarray import EncArray
from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecoderUtils
import numpy as np
from tqdm import tqdm

class Linear_Regression:
    def __init__(self, decoder_utils, encode_utils: FractionalEncoderUtils, lr=0.2, n_iter=100):
        self.encode_utils = encode_utils
        self.lr = lr
        self.n_iter = n_iter
        self.weigths = None
        self.decoder_utils = decoder_utils

    def fit_unencrypted(self, X, y):
        X = np.array(X)
        y = np.array(y)

        self.weigths = np.array(X.shape[1] * [0.0])
        coef = np.array(X.shape[1] * [self.lr / X.shape[0]])

        for it in (range(self.n_iter)):
            gradient = []
            for j in range(X.shape[1]):
                loss = []
                for i in range(X.shape[0]):
                    loss.append(((self.weigths * X[i]).sum() - y[i][0]))
                loss = np.array(loss)
                gradient.append((loss * X.T[j]).sum())
            gradient = np.array(gradient)
            print(f'Iteration: {it}. Gradient: {gradient}')

            self.weigths = self.weigths - coef * gradient
        print(f'Real result: {((X.T@X) @X.T @ y).T}')

    def fit(self, X: EncArray, y: EncArray, decode_utils: FractionalDecoderUtils):
        result = (X.T @ X)@X.T@y
        self.print_noise(decode_utils.decryptor, result[0].enc_arr)
        self.weigths = result

        # self.weigths = EncArray(X.shape[1] * [0.0], enc_utils=self.encode_utils)
        # coef = EncArray(X.shape[1] * [self.lr / X.shape[0]], enc_utils=self.encode_utils)
        #
        # for it in (range(self.n_iter)):
        #     gradient = []
        #     for j in range(X.shape[1]):
        #         loss = []
        #         for i in range(X.shape[0]):
        #             loss.append(((self.weigths * X[i]).sum() - y[i][0]).enc_arr)
        #         loss = EncArray(loss, enc_utils=self.encode_utils, is_encrypted=True)
        #         gradient.append((loss * X.T[j]).sum().enc_arr)
        #     gradient = EncArray(gradient, enc_utils=self.encode_utils, is_encrypted=True)
        #     self.print_noise(decode_utils.decryptor, gradient.enc_arr)
        #     print(f'Iteration: {it}. Gradient: {gradient.decrypt_array(decode_utils)}')
        #     self.weigths = self.weigths - coef * gradient


    def predict(self, X):
        pass

    def print_noise(self, decryptor, res_arr):
        print("Noise budget in encryption: " + (str)(decryptor.invariant_noise_budget(res_arr[0])) + " bits")


context = FracContext()
encode_utils = FractionalEncoderUtils(context)
decode_utils = FractionalDecoderUtils(context)

a = EncArray([[1, 2, -1, 2, 4, -1, 1, 3, -.5, 0, 2, -1.7]], encode_utils).T
X, y = ARMA.create_design_matrix(a, lag=4)

model = Linear_Regression(decode_utils, encode_utils, n_iter=30)
model.fit_unencrypted(X.decrypt_array(decode_utils), y.decrypt_array(decode_utils))
print(f'Estimated result: {model.weigths}')
model.fit(X, y, decode_utils)
print(f'Estimated result: {model.weigths.decrypt_array(decode_utils)}')
