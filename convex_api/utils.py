"""

    Utils  - address conversions

"""

from eth_utils import (
    add_0x_prefix,
    encode_hex,
    remove_0x_prefix,
    is_hexstr,
)

from eth_utils.crypto import keccak


def is_address_hex(address):
    if is_hexstr(address):
        address_base = remove_0x_prefix(address)
        if len(address_base) == 64:
            return True
    return False

def is_address(address):
    if is_address_checksum(address):
        return True
    elif is_address_hex(address):
        return True
    return False


def to_address_checksum(address):
    address_clean = remove_0x_prefix(address.lower())
    address_hash = remove_0x_prefix(encode_hex(keccak(text=address_clean)))
    checksum = ''
    hash_index = 0
    for value in address_clean:
        if int(address_hash[hash_index], 16) > 7:
            checksum += value.upper()
        else:
            checksum += value
        hash_index += 1
        if hash_index >= len(address_hash):
            hash_index = 0
    return add_0x_prefix(checksum)


def is_address_checksum(address):
    return remove_0x_prefix(address) and remove_0x_prefix(address) == remove_0x_prefix(to_address_checksum(address))
