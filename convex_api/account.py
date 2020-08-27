"""

    Account class for convex api


"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from eth_utils import (
    to_bytes,
    to_hex
)


class Account:

    def __init__(self, private_key):
        self._private_key = private_key
        self._public_key = private_key.public_key()

    def sign(self, hash_text):
        hash_data = to_bytes(hexstr=hash_text)
        signed_hash_bytes = self._private_key.sign(hash_data)
        return to_hex(signed_hash_bytes)

    @property
    def address(self):
        public_key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return to_hex(public_key_bytes)

    @staticmethod
    def create_new():
        return Account(Ed25519PrivateKey.generate())

    @staticmethod
    def create_from_bytes(value):
        return Account(Ed25519PrivateKey.from_private_bytes(value))
