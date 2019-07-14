from src.fractions_utils import Fractionals_utils
import numpy as np
from copy import deepcopy


class EncArray:
    def __init__(self, arr, futils):
        self.utils = futils
        self.shape = np.shape(arr)
        self.enc_arr = deepcopy(arr)
        self._recur_apply(arr, fun=self.utils.encrypt_num)

    def _recur_apply(self, *args, fun, cnt=0):

        arr = args[0]
        arr2 = None
        if len(args) == 2:
            arr2 = args[1]

        for i in range(len(arr)):
            if type(arr[i]) == list:
                if arr2 is not None:
                    self._recur_apply(arr[i], arr2, fun=fun, cnt=cnt)
                else:
                    self._recur_apply(arr[i], fun=fun, cnt=cnt)
                cnt += 1
            else:
                if len(self.shape) == 1:
                    if arr2 is not None:
                        self.enc_arr[i] = fun(arr[i], arr2[i])
                    else:
                        self.enc_arr[i] = fun(arr[i])
                else:
                    if arr2 is not None:
                        self.enc_arr[cnt][i] = fun(arr[i], arr2[cnt][i])
                    else:
                        self.enc_arr[cnt][i] = fun(arr[i])

    def __mul__(self, o):
        # elementwise
        self._recur_apply(self.enc_arr, o.get_array(), fun=self.utils.multiply)
        return self.enc_arr

    def __add__(self, o):
        self._recur_apply(self.enc_arr, o.get_array(), fun=self.utils.add)
        return self.enc_arr

    def get_array(self):
        return self.enc_arr

    def __sub__(self, o):
        self._recur_apply(self.enc_arr, o.get_array(), fun=self.utils.substract)
        return self.enc_arr

    def _is_dim_equal(self, o):
        n, m = self.__len__()
        if n == self.shape[0] and m == self.shape[1]:
            return True
        print("Dimensions are not equal!")
        return False

    def __len__(self):
        return self.shape
