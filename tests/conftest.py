"""

    Conftest.py

"""

import logging
import secrets

import pytest

from convex_api.account import Account
from convex_api.api import API
from convex_api.key_pair import KeyPair
from tests.types import KeyPairInfo


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.INFO)

PRIVATE_TEST_KEY = 0x973f69bcd654b264759170724e1e30ccd2e75fc46b7993fd24ce755f0a8c24d0
PUBLIC_KEY = '0x5288Fec4153b702430771DFAC8AeD0B21CAFca4344daE0d47B97F0bf532b3306'
PRIVATE_KEY_MNEMONIC = 'now win hundred protect enroll cram stone come inch ill method often common quiz balance hundred negative truck crime turkey vague ecology nation balcony'   # noqa: E501

PRIVATE_TEST_KEY_TEXT = """
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIGbMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAi3qm1zgjCO5gICCAAw
DAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEENjvj1nzc0Qy22L+Zi+n7yIEQMLW
o++Jzwlcg3PbW1Y2PxicdFHM3dBOgTWmGsvfZiLhSxTluXTNRCZ8ZLL5pi7JWtCl
JAr4iFzPLkM18YEP2ZE=
-----END ENCRYPTED PRIVATE KEY-----
"""
PRIVATE_TEST_KEY_PASSWORD = 'secret'

REGISTER_ACCOUNT_KEY = 0xb1caefd8c8764dc8e04a41ea164bb6aa22572c40729318c7ad766ae44fa13b27
GOVERNANCE_ADDRESS = 6

CONVEX_URL = 'http://localhost:8080'

TEST_ACCOUNT_NAME = 'test.convex-api'


@pytest.fixture(scope='module')
def test_key_pair_info() -> KeyPairInfo:
    return {
        'private_hex': PRIVATE_TEST_KEY,
        'private_bytes': KeyPair.to_bytes(PRIVATE_TEST_KEY),
        'private_text': PRIVATE_TEST_KEY_TEXT,
        'private_password': PRIVATE_TEST_KEY_PASSWORD,
        'private_mnemonic': PRIVATE_KEY_MNEMONIC,
        'register_account_key':  KeyPair.to_bytes(REGISTER_ACCOUNT_KEY),
        'register_account_address': GOVERNANCE_ADDRESS,
        'public_key': PUBLIC_KEY,
    }


@pytest.fixture(scope='module')
def test_key_pair(test_key_pair_info: KeyPairInfo):
    key_pair = KeyPair.import_from_bytes(test_key_pair_info['private_bytes'])
    return key_pair


@pytest.fixture(scope='module')
def test_account(convex: API, test_key_pair: KeyPair, register_account: Account):
    test_account_name = f'{TEST_ACCOUNT_NAME}.{secrets.token_hex(8)}'
    account = convex.setup_account(test_account_name, test_key_pair, register_account)
    if account is not None:
        convex.topup_account(account)
        print(f'public key for test account {account.public_key}')
        return account


@pytest.fixture(scope='module')
def convex_url():
    return CONVEX_URL


@pytest.fixture(scope='module')
def convex(convex_url: str):
    api = API(convex_url)
    return api


@pytest.fixture(scope='module')
def other_account(convex: API):
    key_pair = KeyPair()
    account = convex.create_account(key_pair)
    convex.topup_account(account)
    return account


@pytest.fixture(scope='module')
def register_account(test_key_pair_info: KeyPairInfo):
    registery_account_pair = KeyPair.import_from_bytes(test_key_pair_info['register_account_key'])
    return Account(registery_account_pair, test_key_pair_info['register_account_address'])
