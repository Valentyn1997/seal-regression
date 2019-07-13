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


class Fractions_utils():
    def __init__(self):
        super(Fractions_utils, self).__init__()

        self.parms = EncryptionParameters()
        self.parms.set_poly_modulus("1x^2048 + 1")
        self.parms.set_coeff_modulus(seal.coeff_modulus_128(2048))
        self.parms.set_plain_modulus(1 << 8)

        self.context = SEALContext(self.parms)
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

    def encode_rationals(self, numbers, encoder):
        # encoding without encryption
        encoded_coefficients = []
        for i in range(len(numbers)):
            encoded_coefficients.append(encoder.encode(numbers[i]))
        return encoded_coefficients

    def encode_num(self, num, encoder):
        # encoding without encryption
        return encoder.encode(num)

    def sum_enc_array(self, array, evaluator):
        encrypted_result = Ciphertext()
        evaluator.add_many(array, encrypted_result)
        return encrypted_result

    def decode(self, encrypted_res, decryptor, encoder):
        plain_result = Plaintext()
        decryptor.decrypt(encrypted_res, plain_result)
        result = encoder.decode(plain_result)
        return result

    def encrypt_rationals(self, rational_numbers, encryptor, encoder, parms):
        # encrypt array of rational numbers
        encrypted_rationals = []
        for i in range(len(rational_numbers)):
            encrypted_rationals.append(Ciphertext(parms))
            encryptor.encrypt(encoder.encode(rational_numbers[i]), encrypted_rationals[i])
        return encrypted_rationals

    def weighted_average(self, encrypted_rationals, encoded_coefficients, encoded_divide_by, evaluator, decryptor):

        for i in range(len(encrypted_rationals)):
            evaluator.multiply_plain(encrypted_rationals[i], encoded_coefficients[i])

        encrypted_result = Ciphertext()
        evaluator.add_many(encrypted_rationals, encrypted_result)
        evaluator.multiply_plain(encrypted_result, encoded_divide_by)

        # How much noise budget do we have left?
        print("Noise budget in result: " + (str)(decryptor.invariant_noise_budget(encrypted_result)) + " bits")

        return encrypted_result

    def enc_substract(self, a, b, encoder, evaluator):
        # a and b should be encrypted
        minus_sign = encoder.encode(-1)
        evaluator.multiply_plain(b, minus_sign)
        evaluator.add(a, b)
        return a

    def encrypt_num(self, value, encoder, encryptor):
        plain = encoder.encode(value)
        encrypted = Ciphertext()
        encryptor.encrypt(plain, encrypted)
        return encrypted
