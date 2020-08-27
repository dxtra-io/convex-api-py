"""

    Test Convex api

"""
import pytest
import secrets

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError

def test_convex_api_request_funds(test_account, convex_url):
    convex = ConvexAPI(convex_url)
    amount = secrets.randbelow(100) + 1
    request_amount = convex.request_funds(test_account, amount)
    assert(request_amount == amount)

def test_convex_api_send_transaction(test_account, convex_url):
    convex = ConvexAPI(convex_url)
    request_amount = convex.request_funds(test_account, 10000000)
    result = convex.send_transaction(test_account, '(map inc [1 2 3 4 5])')
    assert 'id' in result
    assert 'value' in result
    assert(result['value'] == [2, 3, 4, 5, 6])

def test_convex_api_get_balance_no_funds(convex_url):
    convex = ConvexAPI(convex_url)
    account = Account.create_new()
    with pytest.raises(ConvexAPIError, match='500'):
        new_balance = convex.get_balance(account)

def test_convex_api_get_balance_insufficent_funds(convex_url):
    convex = ConvexAPI(convex_url)
    account = Account.create_new()
    amount = 100
    request_amount = convex.request_funds(account, amount)
    with pytest.raises(ConvexAPIError, match='FUNDS'):
        new_balance = convex.get_balance(account)

def test_convex_api_get_balance_new_account(convex_url):
    convex = ConvexAPI(convex_url)
    account = Account.create_new()
    amount = 8000000
    request_amount = convex.request_funds(account, amount)
    assert(request_amount == amount)
    new_balance = convex.get_balance(account)
    assert(new_balance == 6000000)
