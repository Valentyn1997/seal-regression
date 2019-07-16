from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecryptorUtils
import numpy as np
from copy import deepcopy
from seal import Ciphertext, Plaintext
from typing import List


class EncArray:
    def __init__(self, arr, enc_utils: FractionalEncoderUtils = None, dtype=Ciphertext):
        """
        Class representing array of encrypted or encoded fractional numbers.
        Support of basic operations applied to an various dimension array.
        :param arr: encrypted/unencrypted or encoded/unencoded array of floats
        :param enc_utils (FractionalEncoderUtils): Fractional utils class providing basic operations on cyphertext
        :param dtype: type of data in array (Plaintext or Ciphertext)

        Examples:
        >> context = FracContext()
        >> encode_utils = FractionalEncoderUtils(context)
        >> a = EncArray([12, 13], encode_utils)
        """
        self.dtype = dtype
        if type(arr) == EncArray:
            self.enc_utils = arr.enc_utils
            self.enc_arr = deepcopy(arr.enc_arr)
        else:
            self.enc_utils = enc_utils
            if dtype == Ciphertext:
                self.enc_arr = self._recur_apply(arr, fun=self.enc_utils.encrypt_num)
            elif dtype == Plaintext:
                self.enc_arr = self._recur_apply(arr, fun=self.enc_utils.encode_num)
            else:
                self.enc_arr = None
                print('Unknown data type!')

        self.shape = np.shape(self.enc_arr)
        self.ndim = len(self.shape)

    @staticmethod
    def _recur_apply(arr1: List, arr2: List = None, fun=None, result=None):
        if result is None:  # First level of recurrence
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
        Element-wise multiplication of 2 encrypted arrays or encrypted and encoded array
        :param o: encrypted array to multiply
        :return: encrypted result
        Example:
        a * b
        """
        if not self._is_shape_equal(o):
            return None
        if self.dtype == Ciphertext and o.dtype == Ciphertext:
            result = self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.multiply)
            # result = self._recur_apply(result, fun=self.enc_utils.relinearize)
        elif self.dtype == Ciphertext and o.dtype == Plaintext:
            result = self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.multiply_plain)
        elif self.dtype == Plaintext and o.dtype == Ciphertext:
            result = self._recur_apply(o.enc_arr, self.enc_arr, fun=self.enc_utils.multiply_plain)
        else:
            print('Not supported opperation')
            result = None
        return EncArray(result, enc_utils=self.enc_utils)

    def __add__(self, o):
        """
        Element-wise sum of 2 encrypted arrays or encrypted and encoded array.
        :param o: encrypted array to add
        :return: encrypted result
        Addition of encrypted arrays.
        Example:
        a + b
        """
        if not self._is_shape_equal(o):
            return None
        if self.dtype == Ciphertext and o.dtype == Ciphertext:
            result = self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.add)

        elif self.dtype == Ciphertext and o.dtype == Plaintext:
            result = self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.add_plain)
        elif self.dtype == Plaintext and o.dtype == Ciphertext:
            result = self._recur_apply(o.enc_arr, self.enc_arr, fun=self.enc_utils.add_plain)
        else:
            print('Not supported opperation')
            result = None
        return EncArray(result, enc_utils=self.enc_utils)

    def __sub__(self, o):
        """
        Substraction of encrypted array from encrypted array
        :param o: Encrypted array to substract
        :return: encrypted result
        Example:
        a - b
        """
        if not self._is_shape_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.subtract), enc_utils=self.enc_utils)

    def _is_shape_equal(self, o):
        if np.array_equal(self.shape, o.shape):
            return True
        print("Dimensions are not equal!")
        return False

    def decrypt_array(self, decode_utils: FractionalDecryptorUtils):
        """
        Decrypts current array object
        :param decode_utils: Decoder class initiliazed with the same context as encoder
        :returns: decrypted array

        Example:
        >> decode_utils = FractionalDecryptorUtils(context)
        >> a.decrypt_array(decode_utils)
        """
        return self._recur_apply(self.enc_arr, fun=decode_utils.decrypt)

    def noise_budget(self, decode_utils: FractionalDecryptorUtils):
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
        return EncArray(self.enc_utils.sum_enc_array(self.enc_arr), enc_utils=self.enc_utils)

    @property
    def T(self):
        """
        Transposed array
        """
        if self.ndim != 1:
            return EncArray(list(map(list, zip(*self.enc_arr))), enc_utils=self.enc_utils)
        else:
            return self

    def __getitem__(self, item):
        """
        Access array elements by index
        """
        return EncArray(self.enc_arr[item], enc_utils=self.enc_utils)

    def __matmul__(self, other):
        """
        Matrix multiplication of 2 encrypted arrays
        :param other: array to multiply
        :return: encrypted result
        Example:
        a @ b
        """
        a = self.enc_arr
        b = other.T.enc_arr

        result = [
            [
                EncArray([(EncArray(ele_a, enc_utils=self.enc_utils) * EncArray(ele_b, enc_utils=self.enc_utils)).enc_arr
                           for ele_a, ele_b in zip(row_a, col_b)], enc_utils=self.enc_utils)
                    .sum()
                    .enc_arr
                for col_b in b]
            for row_a in a
        ]
        return EncArray(result, enc_utils=self.enc_utils)

    def mem_size(self) -> int:
        """
        Sum of all ciphertexts' sizes in array. Note, that the size of freshly ecrypted plaintext always equals to 2.
        :return: Overall size of array
        """
        sizes = np.array(self._recur_apply(self.enc_arr, fun=lambda num: num.size()))
        return sizes.sum()
