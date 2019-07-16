import seal
from seal import EvaluationKeys, Ciphertext, Decryptor, Encryptor, EncryptionParameters, Evaluator, FractionalEncoder, \
    KeyGenerator, Plaintext, SEALContext
from typing import List
from copy import deepcopy


class FracContext:
    primes = [
        0xffffffffffc0001, 0xfffffffff840001, 0xfffffffff240001, 0xffffffffe7c0001,
        0xffffffffe740001, 0xffffffffe4c0001, 0xffffffffe440001, 0xffffffffe400001,
        0xffffffffdbc0001, 0xffffffffd840001, 0xffffffffd680001, 0xffffffffd000001,
        0xffffffffcf00001, 0xffffffffcdc0001, 0xffffffffcc40001, 0xffffffffc300001,
        0xffffffffbf40001, 0xffffffffbdc0001, 0xffffffffb880001, 0xffffffffaec0001,
        0xffffffffa380001, 0xffffffffa200001, 0xffffffffa0c0001, 0xffffffff9600001,
        0xffffffff91c0001, 0xffffffff8f40001, 0xffffffff8680001, 0xffffffff7e40001,
        0xffffffff7bc0001, 0xffffffff76c0001, 0xffffffff7680001, 0xffffffff6fc0001,
        0xffffffff6880001, 0xffffffff6340001, 0xffffffff5d40001, 0xffffffff54c0001,
        0xffffffff4d40001, 0xffffffff4380001, 0xffffffff3e80001, 0xffffffff37c0001,
        0xffffffff36c0001, 0xffffffff2100001, 0xffffffff1d80001, 0xffffffff1cc0001,
        0xffffffff1900001,  0xffffffff1740001,  0xffffffff15c0001,  0xffffffff0e80001,
        0xfffffffeff80001,  0xfffffffeff40001,  0xfffffffeefc0001,  0xfffffffee8c0001,
        0xfffffffede40001,  0xfffffffedcc0001,  0xfffffffed040001,  0xfffffffecf40001,
        0xfffffffecec0001,  0xfffffffecb00001,  0xfffffffec380001,  0xfffffffebb40001
    ]

    def __init__(self, poly_modulus="1x^1024 + 1", coef_modulus_n_primes=20, plain_modulus=1 << 32):
        """
        Set up encryption context for encoder and decoder
        :param poly_modulus:
        :param coef_modulus_n_primes:
        :param plain_modulus:
        """
        self.params = EncryptionParameters()
        self.params.set_poly_modulus(poly_modulus)
        self.params.set_coeff_modulus([seal.SmallModulus(p) for p in FracContext.primes[:coef_modulus_n_primes]])
        self.params.set_plain_modulus(plain_modulus)

        self.context = SEALContext(self.params)
        self.print_parameters(self.context)

        self.keygen = KeyGenerator(self.context)
        self.public_key = self.keygen.public_key()
        self.secret_key = self.keygen.secret_key()
        self.evaluator = Evaluator(self.context)

    def print_parameters(self, context: SEALContext):
        """
        Parameters description
        :param context: SEALContext object
        """
        print("/ Encryption parameters:")
        print("| poly_modulus: " + context.poly_modulus().to_string())

        # Print the size of the true (product) coefficient modulus
        print("| coeff_modulus_size: " + (str)(context.total_coeff_modulus().significant_bit_count()) + " bits")

        print("| plain_modulus: " + (str)(context.plain_modulus().value()))
        print("| noise_standard_deviation: " + (str)(context.noise_standard_deviation()))


class FractionalDecryptorUtils:
    def __init__(self, context):
        """
        Class providing decryption operation
        :param context: Context initialising HE parameters
        """
        self.context = context.context
        self.secret_key = context.secret_key
        self.decryptor = Decryptor(self.context, self.secret_key)
        self.encoder = FractionalEncoder(self.context.plain_modulus(),
                                         self.context.poly_modulus(),
                                         64, 32, 3)
        self.evaluator = context.evaluator

    def decrypt(self, encrypted_res):
        plain_result = Plaintext()
        self.decryptor.decrypt(encrypted_res, plain_result)
        result = self.encoder.decode(plain_result)
        return result


class FractionalEncoderUtils:
    def __init__(self, context: FracContext):
        """
        Class providing encoding and encryption operations, operations over
        encrypted data
        :param context: Context initialising HE parameters
        """
        self.context = context.context
        self.public_key = context.public_key
        self.encryptor = Encryptor(self.context, self.public_key)
        self.encoder = FractionalEncoder(self.context.plain_modulus(),
                                         self.context.poly_modulus(),
                                         64, 32, 3)
        self.evaluator = context.evaluator
        self.ev_keys = EvaluationKeys()
        context.keygen.generate_evaluation_keys(seal.dbc_max(), self.ev_keys)

    def encode_rationals(self, numbers) -> List[Plaintext]:
        # encoding without encryption
        encoded_coefficients = []
        for i in range(len(numbers)):
            encoded_coefficients.append(self.encoder.encode(numbers[i]))
        return encoded_coefficients

    def encode_num(self, num) -> Plaintext:
        if type(num) == Plaintext or num is None:
            return num
        else:  # encoding without encryption
            return self.encoder.encode(num)

    def sum_enc_array(self, array: List[Ciphertext]) -> Ciphertext:
        # can applied for 1D array only
        encrypted_result = Ciphertext()
        self.evaluator.add_many(array, encrypted_result)
        return encrypted_result

    def encrypt_rationals(self, rational_numbers: List) -> List[Ciphertext]:
        """
        :param rational_numbers: array of rational numbers
        :return: encrypted result
        """
        encrypted_rationals = []
        for i in range(len(rational_numbers)):
            encrypted_rationals.append(Ciphertext(self.context.params))
            self.encryptor.encrypt(self.encoder.encode(rational_numbers[i]), encrypted_rationals[i])
        return encrypted_rationals

    def weighted_average(self, encrypted_rationals, encoded_coefficients, encoded_divide_by) -> Ciphertext:
        """
        Weighted average, where weights encoded, not encrypted numbers
        :param encoded_divide_by: fixed point fractional, e.g 0.1 to perform division by 10
        :return: encrypted result
        """
        for i in range(len(encrypted_rationals)):
            self.evaluator.multiply_plain(encrypted_rationals[i], encoded_coefficients[i])

        encrypted_result = Ciphertext()
        self.evaluator.add_many(encrypted_rationals, encrypted_result)
        self.evaluator.multiply_plain(encrypted_result, encoded_divide_by)

        return encrypted_result

    def subtract(self, a: Ciphertext, b: Ciphertext) -> Ciphertext:
        """
        Substruction operation of 2 fractional numbers
        :param a: encrypted fractional value
        :param b: encrypted fractional value
        :return: substracted result
        """
        a = deepcopy(a)
        minus_sign = self.encoder.encode(-1)
        self.evaluator.multiply_plain(b, minus_sign)
        self.evaluator.add(a, b)
        return a

    def encrypt_num(self, value) -> Ciphertext:
        if type(value) == Ciphertext or value is None:
            return value
        else:
            encrypted = Ciphertext()
            if type(value) == Plaintext:
                self.encryptor.encrypt(value, encrypted)
            else:
                plain = self.encoder.encode(value)
                self.encryptor.encrypt(plain, encrypted)
            return encrypted

    def add(self, a: Ciphertext, b: Ciphertext) -> Ciphertext:
        """
        :param a: encrypted fractional value
        :param b: encrypted fractional value
        :return: encrypted sum of a and b
        """
        a = deepcopy(a)
        self.evaluator.add(a, b)
        return a

    def add_plain(self, a: Ciphertext, b: Plaintext) -> Ciphertext:
        """
        :param a: encrypted fractional value
        :param b: encoded fractional value
        :return: encrypted sum of a and b
        """
        a = deepcopy(a)
        self.evaluator.add_plain(a, b)
        return a

    def multiply(self, a: Ciphertext, b: Ciphertext) -> Ciphertext:
        """
        :param a: encrypted fractional value
        :param b: encrypted fractional value
        :return: encrypted product of a and b
        """
        a = deepcopy(a)
        self.evaluator.multiply(a, b)
        return a

    def multiply_plain(self, a: Ciphertext, b: Plaintext) -> Ciphertext:
        """
        :param a: encrypted fractional value
        :param b: encrypted fractional value
        :return: encrypted product of a and b
        """
        a = deepcopy(a)
        self.evaluator.multiply_plain(a, b)
        return a

    def relinearize(self, a: Ciphertext) -> Ciphertext:
        """
        :param a: encrypted fractional value, supposedly result of multiplication
        :return: relinearized a
        """
        a = deepcopy(a)
        self.evaluator.relinearize(a, self.ev_keys)
        return a
