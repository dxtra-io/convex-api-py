"""
    Test account based functions

"""

from convex_api import (
    Account,
    ConvexAPI,
    KeyPair,
)

TEST_ACCOUNT_NAME = 'test.convex-api'

def test_account_api_create_account(convex_url):

    convex = ConvexAPI(convex_url)
    key_pair = KeyPair.create()
    result = convex.create_account(key_pair)
    assert(result)


def test_account_api_multi_create_account(convex_url):
    convex = ConvexAPI(convex_url)
    key_pair = KeyPair.create()
    account_1 = convex.create_account(key_pair)
    assert(account_1)
    account_2 = convex.create_account(key_pair)
    assert(account_2)

    assert(account_1.public_key == account_1.public_key)
    assert(account_1.public_key == account_2.public_key)
    assert(account_1.is_address)
    assert(account_1.address != account_2.address)


def test_account_name(convex_url, test_key_pair_info):
    convex = ConvexAPI(convex_url)
    import_key_pair = KeyPair.import_from_bytes(test_key_pair_info['private_bytes'])
    if convex.resolve_account_name(TEST_ACCOUNT_NAME):
        account = convex.load_account(TEST_ACCOUNT_NAME, import_key_pair)
    else:
        account = convex.create_account(import_key_pair)
        convex.topup_account(account)
        account = convex.register_account_name(TEST_ACCOUNT_NAME, account)
    assert(account.address)
    assert(account.name)
    assert(account.name == TEST_ACCOUNT_NAME)
    assert(convex.resolve_account_name(TEST_ACCOUNT_NAME) == account.address)


def test_account_setup_account(convex_url, test_key_pair_info):
    convex = ConvexAPI(convex_url)
    import_key_pair = KeyPair.import_from_bytes(test_key_pair_info['private_bytes'])
    account = convex.setup_account(TEST_ACCOUNT_NAME, import_key_pair)
    assert(account.address)
    assert(account.name)
    assert(account.name == TEST_ACCOUNT_NAME)
    assert(convex.resolve_account_name(TEST_ACCOUNT_NAME) == account.address)
