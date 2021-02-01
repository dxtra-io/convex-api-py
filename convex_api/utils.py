"""

    Utils  - address conversions

"""
import re

from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives import hashes

from eth_utils import (
    add_0x_prefix,
    is_hexstr,
    remove_0x_prefix,
    to_bytes,
    to_hex
)

def to_address(text):
    if isinstance(text, int):
        return int(text)
    if isinstance(text, str):
        try:
            value = int(re.sub('^#', '', text.strip()))
        except ValueError:
            return None
        return value
    return None

def is_address(text):
    value = to_address(text)
    if isinstance(value, int):
        return value >= 0
    return False

def is_public_key_hex(public_key):
    if is_hexstr(public_key):
        address_base = remove_0x_prefix(public_key)
        if len(address_base) == 64:
            return True
    return False


def is_public_key(public_key):
    if is_public_key_checksum(public_key):
        return True
    if is_public_key_hex(public_key):
        return True
    return False


def to_public_key_checksum(public_key):
    digest = hashes.Hash(hashes.SHA3_256(), backend=backend)
    digest.update(to_bytes(hexstr=public_key))
    public_key_hash = remove_0x_prefix(to_hex(digest.finalize()))
    public_key_clean = remove_0x_prefix(public_key.lower())
    checksum = ''
    hash_index = 0
    for value in public_key_clean:
        if int(public_key_hash[hash_index], 16) > 7:
            checksum += value.upper()
        else:
            checksum += value
        hash_index += 1
        if hash_index >= len(public_key_hash):
            hash_index = 0
    return add_0x_prefix(checksum)


def is_public_key_checksum(public_key):
    return remove_0x_prefix(public_key) and remove_0x_prefix(public_key) == remove_0x_prefix(to_public_key_checksum(public_key))
