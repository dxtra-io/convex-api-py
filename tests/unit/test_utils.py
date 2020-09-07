"""


    Test  Utils

"""
import secrets

from eth_utils import (
    to_checksum_address
)

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
    address = secrets.token_hex(40)
    address_checksum = to_address_checksum(address)
    assert(is_address_checksum(address_checksum))


def test_utils_to_address_checksum():
    # generate a ethereum address
    address = secrets.token_hex(20)
    # convex address to checksum
    address_checksum = to_address_checksum(address)

    # eth utlis address to checksum
    address_ether_checksum = to_checksum_address(address)
    assert(is_address_checksum(address_checksum))
    assert(address_ether_checksum == address_checksum)
