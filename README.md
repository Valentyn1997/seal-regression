# seal-regression

The aim of our work is to perform Machine Learning (ML) algorithm, namely Linear Regression, on the ciphertext and evaluate its performance and usability. We use gradient descent in order to find LR coefficient estimates, as this algorithm does not require division.

![secure ML](https://github.com/Valentyn1997/seal_regression/raw/master/secure_ML_scheme.png)

We used [Microsoft SEAL C++ library](https://www.microsoft.com/en-us/research/project/microsoft-seal/) and its Python wrapper - [PySEAL](https://github.com/Lab41/PySEAL). SEAL uses the Fan-Vercauteren homomorphic encryption scheme - Somewhat Fully Homomorphic scheme.

### Installation for Linux/Mac
```
pip3 install git+https://github.com/Valentyn1997/seal_regression.git
```
One also needs to install [PySEAL Python Library](https://github.com/Lab41/PySEAL). You can run the following script:
```
install_pyseal.sh
```

### Usage examples

The basic example of library usage could be found in: [main.py](seal_regression/main.py).

The perfromance evaluation is in: [perfromance_results.ipynb](https://github.com/Valentyn1997/seal_regression/blob/master/notebooks/perfromance_results.ipynb).
