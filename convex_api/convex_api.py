"""


    Convex

"""

import json
import logging
from urllib.parse import urljoin
import requests


from eth_utils import remove_0x_prefix

from convex_api.exceptions import ConvexAPIError

logger = logging.getLogger(__name__)


class ConvexAPI:
    def __init__(self, url):
        self._url = url

    def send(self, account, transaction):
        if not transaction:
            raise ValueError('You need to provide a valid transaction')
        if not isinstance(transaction, str):
            raise TypeError('The transaction must be a type str')

        hash_data = self._prepare_transaction(account.address, transaction)
        signed_data = account.sign(hash_data['hash'])
        result = self._submit_transaction(account.address, hash_data['hash'], signed_data)
        return result

    def request_funds(self, account, amount):
        faucet_url = urljoin(self._url, '/api/v1/faucet')
        faucet_data = {
            'address': remove_0x_prefix(account.address),
            'amount': amount
        }
        logger.debug(f'send facuet request {faucet_url} {faucet_data}')
        response = requests.post(faucet_url, data=json.dumps(faucet_data))
        if response.status_code != 200:
            raise ConvexAPIError(f'request funds: {response.status_code} {response.text}')
        result = response.json()
        logger.debug(f'request funds result {result}')
        if result['address'] != remove_0x_prefix(account.address):
            raise ConvexAPIError(f'returned account is not correct {result["address"]}')
        return result['amount']

    def get_balance(self, account):
        address = remove_0x_prefix(account.address)
        result = self.send(account, f'(balance "{address}")')
        if 'value' not in result:
            raise ConvexAPIError('Cannot find returned balance value')

        return result['value']

    def _prepare_transaction(self, address, transaction):
        prepare_url = urljoin(self._url, '/api/v1/transaction/prepare')
        data = {
            'address': remove_0x_prefix(address),
            'source': transaction,
        }
        logger.debug(f'prepare transaction {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexAPIError(f'prepare transaction: {response.status_code} {response.text}')

        result = response.json()
        logger.debug(f'prepare repsonse {result}')
        return result

    def _submit_transaction(self, address, hash_data, signed_data):
        submit_url = urljoin(self._url, '/api/v1/transaction/submit')
        data = {
            'address': remove_0x_prefix(address),
            'hash': hash_data,
            'sig': remove_0x_prefix(signed_data)
        }
        logger.debug(f'submit transaction {submit_url} {data}')
        response = requests.post(submit_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexAPIError(f'submit transaction: {response.status_code} {response.text}')
        result = response.json()
        logger.debug(f'submit repsonse {result}')
        if 'error-code' in result:
            raise ConvexAPIError(f'submit transaction error: {result["error-code"]}')
        return result
