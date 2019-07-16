from src.fractions_utils import Fractionals_utils

def main():
    futils = Fractionals_utils()

    coefficients = [0.1, 0.05, 0.05, 0.2, 0.05, 0.3, 0.1, 0.025, 0.075, 0.05]
    rational_numbers = [3.1, 4.159, 2.65, 3.5897, 9.3, 2.3, 8.46, 2.64, 3.383, 2.795]

    encrypted_rationals = futils.encrypt_rationals(rational_numbers)
    encoded_coefficients = futils.encode_rationals(coefficients)
    divide_by = futils.encode_num(1 / len(rational_numbers))

    avg = futils.weighted_average(encrypted_rationals, encoded_coefficients, divide_by)

    print(futils.decode(avg))

    numbers = [3, 4.159, 2.65, 2, -9.3]

    enc_all_nums = futils.encrypt_rationals(numbers)
    enc_sum1 = futils.sum_enc_array(enc_all_nums)
    print(futils.decode(enc_sum1))

    a = futils.encrypt_num(5)
    b = futils.encrypt_num(3)
    res = futils.subtract(a, b)
    print(futils.decode(res))

if __name__ == '__main__':
    main()