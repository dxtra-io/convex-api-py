"""

    Account class for convex api


"""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from eth_utils import (
    remove_0x_prefix,
    to_bytes,
    to_hex
)


class Account:

    def __init__(self, private_key):
        """
        Create a new account with a private key as a Ed25519PrivateKey

        :param Ed25519PrivateKey private_key: The public/private key as an Ed25519PrivateKey object

        """
        self._private_key = private_key
        self._public_key = private_key.public_key()

    def sign(self, hash_text):
        """
        Sign a hash text using the private key.

        :param str hash_text: Hex string of the hash to sign

        :returns: Hex string of the signed text

        """
        hash_data = to_bytes(hexstr=hash_text)
        signed_hash_bytes = self._private_key.sign(hash_data)
        return to_hex(signed_hash_bytes)

    def export_to_text(self, password):
        """
        Export the private key to an encrypted PEM string.

        :param str password: Password to encrypt the private key value

        :returns: The private key as a PEM formated encrypted string

        """
        if isinstance(password, str):
            password = password.encode()
        private_data = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return private_data.decode()

    def export_to_file(self, filename, password):
        """
        Export the private key to a file. This uses `export_to_text` to export as a string.
        Then saves this in a file.

        :param str filename: Filename to create with the PEM string
        :param str password: Password to use to encypt the private key

        """
        with open(filename, 'w') as fp:
            fp.write(self.export_to_text(password))

    def __str__(self):
        return f'Account {self.address}'

    @property
    def address(self):
        """
        Return the public address of the account in the format '0x....'

        :returns: str Address with leading '0x'

        """
        public_key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return to_hex(public_key_bytes)

    @property
    def address_clean(self):
        """
        Return the public address of the account without the leading '0x'

        :returns: str Address without the leading '0x'

        """
        return remove_0x_prefix(self.address)

    @staticmethod
    def create_new():
        """
        Create a new account with a random key and address

        :returns: New Account object

        """
        return Account(Ed25519PrivateKey.generate())

    @staticmethod
    def create_from_bytes(value):
        """
        Create the an account from a private key in bytes.

        :returns: Account object with the private/public key

        """
        return Account(Ed25519PrivateKey.from_private_bytes(value))

    @staticmethod
    def import_from_text(text, password):
        """
        Import an accout from an encrypted PEM string.

        :param str text: PAM text string with the encrypted key text
        :param str password: password to decrypt the private key

        :returns: Account object with the public/private key

        """
        if isinstance(password, str):
            password = password.encode()
        if isinstance(text, str):
            text = text.encode()

        private_key = serialization.load_pem_private_key(text, password, backend=default_backend())
        if private_key:
            return Account(private_key)

    @staticmethod
    def import_from_file(filename, password):
        """
        Load the encrypted private key from file. The file is saved in PEM format encrypted with a password

        :param str filename: Filename to read
        :param str password: password to decrypt the private key

        :returns: Account with the private/public key

        """
        with open(filename, 'r') as fp:
            return Account.import_from_text(fp.read(), password)
