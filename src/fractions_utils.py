import seal
from seal import ChooserEvaluator, \
    Ciphertext, \
    Decryptor, \
    Encryptor, \
    EncryptionParameters, \
    Evaluator, \
    IntegerEncoder, \
    FractionalEncoder, \
    KeyGenerator, \
    MemoryPoolHandle, \
    Plaintext, \
    SEALContext, \
    EvaluationKeys, \
    GaloisKeys, \
    PolyCRTBuilder, \
    ChooserEncoder, \
    ChooserEvaluator, \
    ChooserPoly


class Fractionals_utils():
    def __init__(self):
        super(Fractionals_utils, self).__init__()

        self.params = EncryptionParameters()
        self.params.set_poly_modulus("1x^2048 + 1")
        self.params.set_coeff_modulus(seal.coeff_modulus_128(2048))
        self.params.set_plain_modulus(1 << 8)

        self.context = SEALContext(self.params)
        self.print_parameters(self.context)

        self.keygen = KeyGenerator(self.context)
        self.public_key = self.keygen.public_key()
        self.secret_key = self.keygen.secret_key()

        self.encryptor = Encryptor(self.context, self.public_key)
        self.evaluator = Evaluator(self.context)
        self.decryptor = Decryptor(self.context, self.secret_key)

        self.encoder = FractionalEncoder(self.context.plain_modulus(),
                                         self.context.poly_modulus(),
                                         64, 32, 3)

    def print_parameters(self, context):
        print("/ Encryption parameters:")
        print("| poly_modulus: " + context.poly_modulus().to_string())

        # Print the size of the true (product) coefficient modulus
        print("| coeff_modulus_size: " + (str)(context.total_coeff_modulus().significant_bit_count()) + " bits")

        print("| plain_modulus: " + (str)(context.plain_modulus().value()))
        print("| noise_standard_deviation: " + (str)(context.noise_standard_deviation()))

    def encode_rationals(self, numbers):
        # encoding without encryption
        encoded_coefficients = []
        for i in range(len(numbers)):
            encoded_coefficients.append(self.encoder.encode(numbers[i]))
        return encoded_coefficients

    def encode_num(self, num):
        # encoding without encryption
        return self.encoder.encode(num)

    def sum_enc_array(self, array):
        encrypted_result = Ciphertext()
        self.evaluator.add_many(array, encrypted_result)
        return encrypted_result

    def decode(self, encrypted_res):
        plain_result = Plaintext()
        self.decryptor.decrypt(encrypted_res, plain_result)
        result = self.encoder.decode(plain_result)
        return result

    def encrypt_rationals(self, rational_numbers):
        """
        :param rational_numbers: array of rational numbers
        :return: encrypted result
        """
        encrypted_rationals = []
        for i in range(len(rational_numbers)):
            encrypted_rationals.append(Ciphertext(self.params))
            self.encryptor.encrypt(self.encoder.encode(rational_numbers[i]), encrypted_rationals[i])
        return encrypted_rationals

    def weighted_average(self, encrypted_rationals, encoded_coefficients, encoded_divide_by):

        for i in range(len(encrypted_rationals)):
            self.evaluator.multiply_plain(encrypted_rationals[i], encoded_coefficients[i])

        encrypted_result = Ciphertext()
        self.evaluator.add_many(encrypted_rationals, encrypted_result)
        self.evaluator.multiply_plain(encrypted_result, encoded_divide_by)

        # How much noise budget do we have left?
        print("Noise budget in result: " + (str)(self.decryptor.invariant_noise_budget(encrypted_result)) + " bits")

        return encrypted_result

    def enc_substract(self, a, b):
        """
        :param a: encrypted fractional value
        :param b: encrypted fractional value
        :return: substracted result
        """
        minus_sign = self.encoder.encode(-1)
        self.evaluator.multiply_plain(b, minus_sign)
        self.evaluator.add(a, b)
        return a

    def encrypt_num(self, value):
        plain = self.encoder.encode(value)
        encrypted = Ciphertext()
        self.encryptor.encrypt(plain, encrypted)
        return encrypted
