"""

    Test Account class

"""
import os
import secrets


from convex_api.account import Account
from convex_api.utils import (
    to_bytes,
    remove_0x_prefix
)



SIGN_HASH_TEXT = '5bb1ce718241bfec110552b86bb7cccf0d95b8a5f462fbf6dff7c48543622ba5'
SIGN_TEXT = '0x7eceffab47295be3891ea745838a99102bfaf525ec43632366c7ec3f54db4822b5d581573aecde94c420554f963baebbf412e4304ad8636886ddfa7b1049f70e'
def test_account_create_new():
    account = Account.create()
    assert(account)
    assert(account.public_key)


def test_account_create_from_bytes(test_account_info):
    account = Account.import_from_bytes(test_account_info['private_bytes'])
    assert(account)
    assert(account.public_key == test_account_info['public_key'].lower())

def test_account_address_bytes(test_account_info):
    account = Account.import_from_bytes(test_account_info['private_bytes'])
    assert(account)
    assert(account.public_key_bytes == to_bytes(hexstr=test_account_info['public_key']))

def test_account_address_api(test_account_info):
    account = Account.import_from_bytes(test_account_info['private_bytes'])
    assert(account)
    assert(account.public_key_api == remove_0x_prefix(test_account_info['public_key']))

def test_account_address_checksum(test_account_info):
    account = Account.import_from_bytes(test_account_info['private_bytes'])
    assert(account)
    assert(account.public_key_checksum == test_account_info['public_key'])

def test_account_sign(test_account_info):
    hash_text = SIGN_HASH_TEXT
    account = Account.import_from_bytes(test_account_info['private_bytes'])
    sign_data = account.sign(hash_text)
    assert(sign_data == SIGN_TEXT)


def test_account_import_export_to_text(test_account):
    password = 'secret'
    text = test_account.export_to_text(password)
    import_account = Account.import_from_text(text, password)
    assert(import_account)
    assert(import_account.public_key == test_account.public_key)


def test_account_import_export_to_file(test_account):
    filename = '/tmp/private_key.pem'
    password = 'secret'
    if os.path.exists(filename):
        os.remove(filename)

    text = test_account.export_to_file(filename, password)
    assert(os.path.exists(filename))
    import_account = Account.import_from_file(filename, password)
    assert(import_account)
    assert(import_account.public_key == test_account.public_key)
    os.remove(filename)

def test_account_export_to_mnemonic(test_account):
    words = test_account.export_to_mnemonic
    assert(words)
    new_account = Account.import_from_mnemonic(words)
    assert(new_account)
    assert(test_account.public_key == new_account.public_key)
    assert(test_account.export_to_mnemonic == new_account.export_to_mnemonic)
