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
