"""
    Test signing to send a transaction

"""
import json
import requests

from eth_utils import to_hex, remove_0x_prefix, to_bytes

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

PRIVATE_TEST_KEY = 0x973f69bcd654b264759170724e1e30ccd2e75fc46b7993fd24ce755f0a8c24d0
PUBLIC_ADDRESS = '5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306'

def test_submit_transaction():


    # private_key = Ed25519PrivateKey.generate()
    private_key = Ed25519PrivateKey.from_private_bytes(to_bytes(PRIVATE_TEST_KEY))

    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_address = remove_0x_prefix(to_hex(public_key_bytes))
    assert(public_address == PUBLIC_ADDRESS)

    faucet_data = {
        'address': public_address,
        'amount': 10000000
    }
    print('faucet send', faucet_data)
    url = 'https://convex.world/api/v1/faucet'
    response = requests.post(url, data=json.dumps(faucet_data))
    if response.status_code != 200:
        print('error', response.text)
        return
    print('faucet response', response.json())

    prepare_data = {
        'address': public_address,
        'source': '(map inc [1 2 3])'
    }
    url = 'https://convex.world/api/v1/transaction/prepare'
    print('prepare send', prepare_data)
    response = requests.post(url, data=json.dumps(prepare_data))
    if response.status_code != 200:
        print('prepare error', response.text)
        return
    print(response.json())

    result = response.json()

    print(result)
    hash_data = to_bytes(hexstr=result['hash'])
    signed_hash_bytes = private_key.sign(hash_data)
    signed_hash = to_hex(signed_hash_bytes)
    submit_data = {
        'address': public_address,
        'hash': result['hash'],
        'sig': remove_0x_prefix(signed_hash)
    }

    url = 'https://convex.world/api/v1/transaction/submit'
    print('submit send', submit_data)
    response = requests.post(url, data=json.dumps(submit_data))
    if response.status_code != 200:
        print('submit error', response.text)
    print(response.json())
