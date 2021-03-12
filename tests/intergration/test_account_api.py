"""
    Test account based functions

"""

from convex_api import (
    Account,
    ConvexAPI
)

TEST_ACCOUNT_NAME = 'test.convex-api'

def test_account_api_create_account(convex_url):

    convex = ConvexAPI(convex_url)
    result = convex.create_account()
    assert(result)


def test_account_api_multi_create_account(convex_url):
    convex = ConvexAPI(convex_url)
    account = Account.create()
    account_1 = convex.create_account(account=account)
    assert(account_1)
    account_2 = convex.create_account(account=account)
    assert(account_2)

    assert(account.public_key == account_1.public_key)
    assert(account.public_key == account_2.public_key)
    assert(not account.is_address)
    assert(account_1.address != account_2.address)


def test_account_name(convex_url, test_account_info):
    convex = ConvexAPI(convex_url)
    import_account = Account.import_from_bytes(test_account_info['private_bytes'])
    if convex.resolve_account_name(TEST_ACCOUNT_NAME):
        account = convex.load_account(TEST_ACCOUNT_NAME, import_account)
    else:
        account = convex.create_account(account=import_account)
        convex.topup_account(account)
        account = convex.register_account_name(TEST_ACCOUNT_NAME, account)
    assert(account.address)
    assert(account.name)
    assert(account.name == TEST_ACCOUNT_NAME)
    assert(convex.resolve_account_name(TEST_ACCOUNT_NAME) == account.address)


def test_account_setup_account(convex_url, test_account_info):
    convex = ConvexAPI(convex_url)
    import_account = Account.import_from_bytes(test_account_info['private_bytes'])
    account = convex.setup_account(TEST_ACCOUNT_NAME, import_account)
    assert(account.address)
    assert(account.name)
    assert(account.name == TEST_ACCOUNT_NAME)
    assert(convex.resolve_account_name(TEST_ACCOUNT_NAME) == account.address)
