from src.fractions_utils import FracContext, FractionalEncoderUtils, FractionalDecryptorUtils
from src.encarray import EncArray
from src.linear_regression import SecureLinearRegression

from sklearn.datasets import make_regression
import numpy as np


def generate_dataset(n_samples, n_features, noise, add_intercept=True):
    X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=noise)
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    if add_intercept:
        X = np.hstack((X, np.ones((X.shape[0], 1))))
    y = (y - np.mean(y)) / np.std(y)
    y = y.reshape(-1, 1)
    return X, y


def main():
    context = FracContext(poly_modulus="1x^1024 + 1", coef_modulus_n_primes=20, plain_modulus=1 << 32)
    encode_utils = FractionalEncoderUtils(context)
    decode_utils = FractionalDecryptorUtils(context)

    X, y = generate_dataset(7, 1, 15)
    X_enc, y_enc = EncArray(X.tolist(), enc_utils=encode_utils), EncArray(y.tolist(), enc_utils=encode_utils)
    print(f'X shape: {X.shape}, y shape: {y.shape}')

    print(f'=========== Simple unencrypted LR ===========')
    model = SecureLinearRegression()
    model.fit_unencrypted(X, y, n_iter=25, verbose=True)
    print(f'Estimated parameters: {model.weigths}')

    print(f'================= Secure LR ==================')
    n_runs = 5
    init_weights = None
    for run in range(n_runs):
        print(f'RUN {run+1}/{n_runs}: ')
        model.fit(X_enc, y_enc, decode_utils, init_weights, n_iter=7, verbose=True)

        weights = model.weigths.decrypt_array(decode_utils)
        print(f'Estimated parameters: {weights}')
        print(f'Prediction: {model.predict(X_enc).decrypt_array(decode_utils)}. Real values: {y.T}')

        # Reencprypting weights
        init_weights = EncArray(weights, enc_utils=encode_utils)


if __name__ == '__main__':
    main()
