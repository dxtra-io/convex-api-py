"""

    Test Account class

"""
import os
import secrets


from convex_api.account import Account
from convex_api.key_pair import KeyPair
from convex_api.utils import (
    to_bytes,
    remove_0x_prefix
)



def test_account_create_new():
    key_pair = KeyPair.create()
    account = Account.create(key_pair, 99)
    assert(account)
    assert(account.public_key)


