"""

    Conftest.py

"""

import logging
import pytest
from eth_utils import to_bytes

from convex_api.account import Account

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.INFO)

PRIVATE_TEST_KEY = 0x973f69bcd654b264759170724e1e30ccd2e75fc46b7993fd24ce755f0a8c24d0
PUBLIC_ADDRESS = '0x5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306'

CONVEX_URL = 'https://convex.world'


@pytest.fixture(scope='module')
def test_account_info():
    return {
        'private_hex' : PRIVATE_TEST_KEY,
        'private_bytes': to_bytes(PRIVATE_TEST_KEY),
        'address': PUBLIC_ADDRESS
    }

@pytest.fixture(scope='module')
def test_account(test_account_info):
    return Account.create_from_bytes(test_account_info['private_bytes'])

@pytest.fixture(scope='module')
def convex_url():
    return CONVEX_URL
