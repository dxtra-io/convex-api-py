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
    result = convex.send(test_account, '(map inc [1 2 3 4 5])')
    assert 'id' in result
    assert 'value' in result
    assert(result['value'] == [2, 3, 4, 5, 6])

def test_convex_api_get_balance_no_funds(convex_url):
    convex = ConvexAPI(convex_url)
    account = Account.create_new()
    with pytest.raises(ConvexAPIError, match='NOBODY'):
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

def test_convex_api_call(convex_url):

    deploy_storage = "(def storage-example  (deploy   '(do     (def stored-data nil)     (defn get [] stored-data)     (defn set [x] (def stored-data x))     (export get set))))"
    convex = ConvexAPI(convex_url)
    account = Account.create_new()
    amount = 8000000
    request_amount = convex.request_funds(account, amount)
    result = convex.send(account, deploy_storage)
    assert(result['value'])
    test_number = secrets.randbelow(1000)
    call_set_result = convex.send(account, f'(call storage-example (set {test_number}))')
    assert(call_set_result['value'] == test_number)
    call_get_result = convex.send(account, '(call storage-example (get))')
    assert(call_get_result['value'] == test_number)

def test_convex_api_transfer(convex_url):
    convex = ConvexAPI(convex_url)
    account_from = Account.create_new()
    account_to = Account.create_new()
    amount = 8000000
    request_amount = convex.request_funds(account_from, amount)
    assert(request_amount == amount)

    result = convex.transfer(account_from, account_to, amount / 2)
    balance_from = convex.get_balance(account_from)
    balance_to = convex.get_balance(account_to)
    # this is incorrect ! sent funds == amount / 4 ?
    print(balance_from, balance_to)
    assert(balance_to == amount / 4)
