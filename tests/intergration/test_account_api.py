"""
    Test account based functions

"""

from convex_api import (
    Account,
    ConvexAPI
)

def test_account_api_create_account(convex_url):

    convex = ConvexAPI(convex_url)
    result = convex.create_account()
    assert(result)


def test_account_api_multi_create_account(convex_url):

    convex = ConvexAPI(convex_url)
    account = Account.create()
    account_1 = convex.create_account(account)
    assert(account_1)
    account_2 = convex.create_account(account)
    assert(account_2)

    assert(account.public_key == account_1.public_key)
    assert(account.public_key == account_2.public_key)
    assert(not account.is_address)
    assert(account_1.address != account_2.address)
