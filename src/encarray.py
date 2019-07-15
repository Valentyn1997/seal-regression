from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecoderUtils
import numpy as np
from copy import deepcopy


class EncArray:
    def __init__(self, arr, enc_utils: FractionalEncoderUtils = None, is_encrypted=False):
        """
        Class representing encrypted array of encrypted fractional numbers.
        Support of basic operations applied to an various dimension array.
        :param arr: encrypted or unencrypted array of floats
        :param enc_utils: Fractional utils class providing
        :param is_encrypted: flag to determine encrypted arr or not

        Examples:
        >> context = FracContext()
        >> encode_utils = FractionalEncoderUtils(context)
        >> a = EncArray([12, 13], encode_utils)
        """
        if type(arr) == EncArray:
            self.enc_utils = arr.enc_utils
            self.enc_arr = deepcopy(arr.enc_arr)
        else:
            self.enc_utils = enc_utils
            if not is_encrypted:
                self.enc_arr = self._recur_apply(arr, fun=self.enc_utils.encrypt_num)
            else:
                self.enc_arr = deepcopy(arr)

        self.shape = np.shape(self.enc_arr)
        self.ndim = len(self.shape)

    @staticmethod
    def _recur_apply(arr1, arr2=None, fun=None, result=None):
        if result is None:
            arr1 = deepcopy(arr1)
            arr2 = deepcopy(arr2)
            result = deepcopy(arr1)

        if type(arr1) != list:
            return fun(arr1, arr2) if arr2 is not None else fun(arr1)
        else:
            result = [
                EncArray._recur_apply(arr1[i], arr2[i], fun=fun, result=result[i]) if arr2 is not None
                else EncArray._recur_apply(arr1[i], fun=fun, result=result[i])
                for i in range(len(arr1))
            ]
            return result

    def __mul__(self, o):
        """
        Element-wise multiplication of 2 encrypted array
        :param o: encrypted array to multiply
        :return: encrypted result
        Example:
        a * b
        """
        if not self._is_dim_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.multiply),
                        enc_utils=self.enc_utils, is_encrypted=True)

    def __add__(self, o):
        """
        :param o: encrypted array to add
        :return: encrypted result
        Addition of encrypted arrays
        Example:
        a + b
        """
        if not self._is_dim_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.add),
                        enc_utils=self.enc_utils, is_encrypted=True)

    def __sub__(self, o):
        """
        Substraction of array from array
        :param o: Encrypted array to substract
        :return: encrypted result
        Example:
        a - b
        """
        if not self._is_dim_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.substract),
                        enc_utils=self.enc_utils, is_encrypted=True)

    def _is_dim_equal(self, o):
        if np.array_equal(self.shape, o.shape):
            return True
        print("Dimensions are not equal!")
        return False

    def decrypt_array(self, decode_utils: FractionalDecoderUtils):
        """
        Decrypts current array object
        :param decode_utils: Decoder class initiliazed with the same context as encoder
        :returns: decrypted array

        Example:
        >> decode_utils = FractionalDecoderUtils(context)
        >> a.decrypt_array(decode_utils)
        """
        return self._recur_apply(self.enc_arr, fun=decode_utils.decode)

    def noise_budget(self, decode_utils: FractionalDecoderUtils):
        """
        Compute noise budget consumption for each encrypted number in an array
        :return: left amount of budget in bits for every element in array
        """
        return self._recur_apply(self.enc_arr, fun=decode_utils.decryptor.invariant_noise_budget)

    def __len__(self):
        return len(self.enc_arr)

    def sum(self):
        """
        Sums of elements of 1D array
        :returns encrypted sum
        """
        return EncArray(self.enc_utils.sum_enc_array(self.enc_arr), enc_utils=self.enc_utils, is_encrypted=True)

    @property
    def T(self):
        if self.ndim != 1:
            return EncArray(list(map(list, zip(*self.enc_arr))), enc_utils=self.enc_utils, is_encrypted=True)
        else:
            return self

    def __getitem__(self, item):
        """
        Access array elements by index
        """
        return EncArray(self.enc_arr[item], enc_utils=self.enc_utils, is_encrypted=True)

    def __matmul__(self, other):
        """
        Matrix multiplication
        :param other: array to multiply
        :return: encrypted result
        Example:
        a @ b
        """
        a = self.enc_arr
        b = other.T.enc_arr

        result = [
            [
                EncArray([(EncArray(ele_a, enc_utils=self.enc_utils, is_encrypted=True) * EncArray(ele_b, enc_utils=self.enc_utils, is_encrypted=True)).enc_arr
                           for ele_a, ele_b in zip(row_a, col_b)], enc_utils=self.enc_utils, is_encrypted=True)
                    .sum()
                    .enc_arr
                for col_b in b]
            for row_a in a
        ]
        return EncArray(result, enc_utils=self.enc_utils, is_encrypted=True)
