from src.fractions_utils import FractionalEncoderUtils, FracContext, FractionalDecoderUtils
import numpy as np
from copy import deepcopy


class EncArray:
    def __init__(self, arr, enc_utils: FractionalEncoderUtils, is_encrypted=False):
        self.enc_utils = enc_utils
        self.shape = np.shape(arr)
        self.ndim = len(self.shape)
        if not is_encrypted:
            self.enc_arr = self._recur_apply(arr, fun=self.enc_utils.encrypt_num)
        else:
            self.enc_arr = deepcopy(arr)
        #self.decryptor = decryptor

    @staticmethod
    def _recur_apply(arr1, arr2=None, fun=None, result=None):
        if result is None:
            arr1 = deepcopy(arr1)
            arr2 = deepcopy(arr2)
            result = deepcopy(arr1)

        if type(arr1) != list:
            return fun(arr1, arr2) if arr2 is not None else fun(arr1)
        else:
            result = [EncArray._recur_apply(arr1[i], arr2[i], fun=fun, result=result[i]) if arr2 is not None
                      else EncArray._recur_apply(arr1[i], fun=fun, result=result[i])
                      for i in range(len(arr1))]
            return result

    def __mul__(self, o):
        # elementwise
        if not self._is_dim_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.multiply),
                        enc_utils=self.enc_utils, is_encrypted=True)

    def __add__(self, o):
        if not self._is_dim_equal(o):
            return None
        return EncArray(self._recur_apply(self.enc_arr, o.enc_arr, fun=self.enc_utils.add),
                        enc_utils=self.enc_utils, is_encrypted=True)

    def __sub__(self, o):
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
        return self._recur_apply(self.enc_arr, fun=decode_utils.decode)

    def __len__(self):
        return len(self.enc_arr)

    def sum(self):
        return EncArray(self.enc_utils.sum_enc_array(self.enc_arr), enc_utils=self.enc_utils, is_encrypted=True)

    @property
    def T(self):
        if self.ndim != 1:
            return EncArray(list(map(list, zip(*self.enc_arr))), enc_utils=self.enc_utils, is_encrypted=True)
        else:
            return self

    def __getitem__(self, item):
        return EncArray(self.enc_arr[item], enc_utils=self.enc_utils, is_encrypted=True)


    def __matmul__(self, other):
        a = self.enc_arr
        b = other.T.enc_arr
        # zip_b = zip(*b)

        result = [[EncArray([
            (EncArray(ele_a, enc_utils=encode_utils, is_encrypted=True) * EncArray(ele_b, enc_utils=encode_utils, is_encrypted=True)).enc_arr for ele_a, ele_b in zip(row_a, col_b)],
            enc_utils=encode_utils, is_encrypted=True).sum().enc_arr
                   for col_b in b] for row_a in a]

        # result = [EncArray([self.enc_utils.multiply(a, b) for a, b in zip(A_row, B_col) for B_col in zip(*other)], enc_utils=self.enc_utils, is_encrypted=True).sum()
        #           for A_row in self.enc_arr]
        return EncArray(result, enc_utils=self.enc_utils, is_encrypted=True)

# # Simple usage
context = FracContext()
encode_utils = FractionalEncoderUtils(context)
decode_utils = FractionalDecoderUtils(context)
#
# a = EncArray(12, encode_utils)
# b = EncArray(10, encode_utils)
# print((a + b).decrypt_array(decode_utils))
#
#
# a = np.array([[10, 11], [13, 14]])
# b = np.array([[10, 10], [10, 10]])
# print(a@b)
#
# a = EncArray([[10, 11], [13, 14]], encode_utils)
# b = EncArray([[10, 10], [10, 10]], encode_utils)
# a1 = EncArray([10, 11, 12], encode_utils)
# b1 = EncArray([13.3, 34, 12], encode_utils)
# a2 = EncArray([10, 11, 12], encode_utils)
# b2 = EncArray([13.3, 34, 12], encode_utils)
#
# c = a1 + b1
# d = a * b
# f = a2 - b2
# g = a @ b
# print(g.decrypt_array(decode_utils))
# print(a1.decrypt_array(decode_utils))
# print(b1.decrypt_array(decode_utils))
#
# sum = a1.sum()
# #print(g.decrypt_array(decode_utils))
#
# print(sum.decrypt_array(decode_utils))
