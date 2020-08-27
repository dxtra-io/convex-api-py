"""

    Test Account class

"""
import secrets

from convex_api.account import Account
from eth_utils import (
    remove_0x_prefix,
    to_bytes,
    to_hex
)


SIGN_HASH_TEXT = '5bb1ce718241bfec110552b86bb7cccf0d95b8a5f462fbf6dff7c48543622ba5'
SIGN_TEXT = '0x7eceffab47295be3891ea745838a99102bfaf525ec43632366c7ec3f54db4822b5d581573aecde94c420554f963baebbf412e4304ad8636886ddfa7b1049f70e'
def test_account_create_new():
    account = Account.create_new()
    assert(account)
    assert(account.address)


def test_account_create_from_bytes(test_account_info):
    account = Account.create_from_bytes(test_account_info['private_bytes'])
    assert(account)
    assert(account.address == test_account_info['address'])
    assert(account.address_clean == remove_0x_prefix(test_account_info['address']))

def test_account_sign(test_account_info):
    hash_text = SIGN_HASH_TEXT
    account = Account.create_from_bytes(test_account_info['private_bytes'])
    sign_data = account.sign(hash_text)
    assert(sign_data == SIGN_TEXT)
