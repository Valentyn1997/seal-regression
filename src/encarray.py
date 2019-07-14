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

    @property
    def T(self):
        if self.ndim != 1:
            return EncArray(list(map(list, zip(*self.enc_arr))), enc_utils=self.enc_utils, is_encrypted=True)
        else:
            return self

    def __getitem__(self, item):
        return EncArray(self.enc_arr[item], enc_utils=self.enc_utils, is_encrypted=True)


# Simple usage
context = FracContext()
encode_utils = FractionalEncoderUtils(context)
decode_utils = FractionalDecoderUtils(context)

a = EncArray([[10, 11, 12], [13, 14, 15]], encode_utils)
b = EncArray([[10, 10, 10], [10, 10, 10]], encode_utils)
a1 = EncArray([10, 11, 12], encode_utils)
b1 = EncArray([13.3, 34, 12], encode_utils)
a2 = EncArray([10, 11, 12], encode_utils)
b2 = EncArray([13.3, 34, 12], encode_utils)

c = a1 + b1
d = a * b
f = a2 - b2
print(c.decrypt_array(decode_utils))
print(a1.decrypt_array(decode_utils))
print(b1.decrypt_array(decode_utils))

print(a1[0])
