"""


    Test  Utils

"""
import secrets

PUBLIC_KEY = '0x5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306'
PUBLIC_KEY_CHECKSUM = '0x5288Fec4153b702430771DFAC8AeD0B21CAFca4344daE0d47B97F0bf532b3306'

from convex_api.utils import (
    is_address,
    is_public_key,
    is_public_key_hex,
    is_public_key_checksum,
    to_address,
    to_public_key_checksum
)

def test_utils_is_public_key_hex():
    public_key = secrets.token_hex(32)
    assert(is_public_key_hex(public_key))

def test_utils_is_public_key():
    public_key = secrets.token_hex(32)
    assert(is_public_key(public_key))

def test_utils_is_public_key_checksum():
    public_key = secrets.token_hex(32)
    public_key_checksum = to_public_key_checksum(public_key)
    assert(is_public_key_checksum(public_key_checksum))

def test_utils_to_public_key_checksum():
    # generate a ethereum public_key
    # convex public_key to checksum
    public_key_checksum = to_public_key_checksum(PUBLIC_KEY)
    assert(is_public_key_checksum(public_key_checksum))
    assert(public_key_checksum == PUBLIC_KEY_CHECKSUM)

def test_utils_is_address():
    address_int = secrets.randbelow(pow(2, 1024)) + 1
    assert(is_address(address_int))

    address_str = str(address_int)
    assert(is_address(address_str))

    address = to_address(f'#{address_str}')
    assert(address == address_int)

    assert(not is_address('test'))
    assert(not is_address(' #'))
    assert(is_address('#0'))
    assert(not is_address('#-1'))
