"""

    Conftest.py

"""

import logging
import pytest
from eth_utils import to_bytes

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.INFO)

PRIVATE_TEST_KEY = 0x973f69bcd654b264759170724e1e30ccd2e75fc46b7993fd24ce755f0a8c24d0
PUBLIC_ADDRESS = '0x5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306'


PRIVATE_TEST_KEY_TEXT = """
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIGbMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAi3qm1zgjCO5gICCAAw
DAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEENjvj1nzc0Qy22L+Zi+n7yIEQMLW
o++Jzwlcg3PbW1Y2PxicdFHM3dBOgTWmGsvfZiLhSxTluXTNRCZ8ZLL5pi7JWtCl
JAr4iFzPLkM18YEP2ZE=
-----END ENCRYPTED PRIVATE KEY-----
"""
PRIVATE_TEST_KEY_PASSWORD = 'secret'

CONVEX_URL = 'https://convex.world'


@pytest.fixture(scope='module')
def test_account_info():
    return {
        'private_hex' : PRIVATE_TEST_KEY,
        'private_bytes': to_bytes(PRIVATE_TEST_KEY),
        'private_text': PRIVATE_TEST_KEY_TEXT,
        'private_password': PRIVATE_TEST_KEY_PASSWORD,
        'address': PUBLIC_ADDRESS
    }

@pytest.fixture(scope='module')
def test_account(test_account_info):
    return Account.import_from_bytes(test_account_info['private_bytes'])

@pytest.fixture(scope='module')
def convex_url():
    return CONVEX_URL

@pytest.fixture(scope='module')
def convex(convex_url):
    api = ConvexAPI(convex_url)
    return api

@pytest.fixture(scope='module')
def other_account(convex):
    account = Account.create()
    convex.topup_account(account)
    return account
