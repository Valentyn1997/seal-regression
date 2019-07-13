from src.fractions_utils import Fractionals_utils

class Array:
    def __init__(self):
        self.utils = Fractionals_utils()

    def array(self, arr):
        n = len(arr)
        m = len(arr[0])
        enc_arr = [[0 for x in range(n)] for y in range(m)]

        for i in range(n):
            for j in range(m):
                enc_arr[n][m] = self.utils.encrypt_num(arr[n][m])
        return 


    def multiply(self):
        pass

    def sum(self):
        pass