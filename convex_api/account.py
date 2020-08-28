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

        """
        self._private_key = private_key
        self._public_key = private_key.public_key()

    def sign(self, hash_text):
        """

        """
        hash_data = to_bytes(hexstr=hash_text)
        signed_hash_bytes = self._private_key.sign(hash_data)
        return to_hex(signed_hash_bytes)

    def export_to_text(self, password):
        """

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

        """
        with open(filename, 'w') as fp:
            fp.write(self.export_to_text(password))

    def __str__(self):
        return f'Account {self.address}'

    @property
    def address(self):
        """

        """
        public_key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return to_hex(public_key_bytes)

    @property
    def address_clean(self):
        """

        """
        return remove_0x_prefix(self.address)

    @staticmethod
    def create_new():
        """

        """
        return Account(Ed25519PrivateKey.generate())

    @staticmethod
    def create_from_bytes(value):
        """

        """
        return Account(Ed25519PrivateKey.from_private_bytes(value))

    @staticmethod
    def import_from_text(text, password):
        """

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

        """
        with open(filename, 'r') as fp:
            return Account.import_from_text(fp.read(), password)
