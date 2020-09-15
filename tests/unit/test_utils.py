"""


    Test  Utils

"""
import secrets

PUBLIC_ADDRESS = '0x5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306'
PUBLIC_ADDRESS_CHECHKSUM = '0x5288Fec4153b702430771DFAC8AeD0B21CAFca4344daE0d47B97F0bf532b3306'

from convex_api.utils import (
    is_address,
    is_address_hex,
    is_address_checksum,
    to_address_checksum
)

def test_utils_is_address_hex():
    address = secrets.token_hex(32)
    assert(is_address_hex(address))

def test_utils_is_address():
    address = secrets.token_hex(32)
    assert(is_address(address))

def test_utils_is_address_checksum():
    address = secrets.token_hex(32)
    address_checksum = to_address_checksum(address)
    assert(is_address_checksum(address_checksum))


def test_utils_to_address_checksum():
    # generate a ethereum address
    # convex address to checksum
    address_checksum = to_address_checksum(PUBLIC_ADDRESS)
    assert(is_address_checksum(address_checksum))
    assert(address_checksum == PUBLIC_ADDRESS_CHECHKSUM)
