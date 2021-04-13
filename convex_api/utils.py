"""

    Utils  - address conversions

"""
import binascii
import re

from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives import hashes


def to_address(text):
    """
    Convert address text with possible leading '#' to an interger address value.

    :param str text: Address text to convert

    :returns: Integer address or None if not a valid address

    """
    if isinstance(text, int):
        return int(text)
    if isinstance(text, str):
        try:
            value = int(re.sub(r'^#', '', text.strip()))
        except ValueError:
            return None
        return value
    return None


def is_address(text):
    """
    Returns True if the text value is a valid address.

    :param str, int text: Possible address field.

    :returns: True if the text field is a valid address.

    """
    value = to_address(text)
    if isinstance(value, int):
        return value >= 0
    return False


def is_public_key_hex(public_key):
    """
    Returns True if the value passed is a valid public key.

    :params str public_key: Public key to check, this has to be a hex string with a possible `0x` at the front.

    :returns: True if the passed value is a valid hex public key.

    """
    if is_hexstr(add_0x_prefix(public_key)):
        address_base = remove_0x_prefix(public_key)
        if len(address_base) == 64:
            return True
    return False


def is_public_key(public_key):
    """
    Returns True if the value passed is a valid public key.

    :params str public_key: Public key to check, this has to be a hex string with a possible `0x` at the front.

    :returns: True if the passed value is a valid hex public key.

    """
    if is_public_key_checksum(public_key):
        return True
    if is_public_key_hex(public_key):
        return True
    return False


def to_public_key_checksum(public_key):
    """
    Convert a public key to a checksum key. This will first make all a-f chars lower case
    then convert a-f chars to uppercase depending on the hash of the public key.

    :params str public_key: Key to convert to a checksum key.

    :returns: Checksum key of the public_key.

    """
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
    """
    Returns True if the public_key passed is a valid checksum.

    :param str public_key: Public key that is in the checksum format

    :returns: True if the key passed has the correct checksum applied to it

    """
    return remove_0x_prefix(public_key) and remove_0x_prefix(public_key) == remove_0x_prefix(to_public_key_checksum(public_key))


def is_hexstr(text):
    """
    Return True if the text passed is a hex string.

    :param str text: Hex chars including the '0x' at the begining.

    :returns: True if all chars are hex
    """
    return re.match('^0x[0-9a-f]+$', text, re.IGNORECASE)


def add_0x_prefix(text):
    """
    Append the 0x prefix to the hex chars

    :param str text: Text to preappend the `0x` too.

    :returns: The text with a `0x` appended to the front

    """
    if text:
        return '0x' + remove_0x_prefix(text)


def remove_0x_prefix(text):
    """
    Removes the '0x' from the front of the hex string.

    :param str text: Hex string to remove the '0x' from.

    :results: Removed '0x' from the hex string.

    """
    if text:
        return re.sub(r'^0x', '', text, re.IGNORECASE)


def to_bytes(data=None, hexstr=None):
    """
    Convert byte data or hexstr to bytes.

    :param bytes, int data: Data to convert to bytes
    :param str hexstr: Hex string to convert to bytes

    :returns Bytes of the hex data

    """
    if data:
        return data.to_bytes(32, 'big')
    elif hexstr and is_hexstr(add_0x_prefix(hexstr)):
        return binascii.unhexlify(remove_0x_prefix(hexstr))


def to_hex(value):
    """
    Convert byte data to hex.

    :params value: data to convert to hex

    :returns: Returns a hex string with a preappended '0x'
    """
    return add_0x_prefix(binascii.hexlify(value).decode())
