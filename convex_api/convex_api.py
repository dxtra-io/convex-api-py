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

        hash_data = self._transaction_prepare(account.address, transaction)
        signed_data = account.sign(hash_data['hash'])
        result = self._transaction_submit(account.address, hash_data['hash'], signed_data)
        return result

    def request_funds(self, account, amount):
        faucet_url = urljoin(self._url, '/api/v1/faucet')
        faucet_data = {
            'address': remove_0x_prefix(account.address),
            'amount': amount
        }
        logger.debug(f'faucet_request {faucet_url} {faucet_data}')
        response = requests.post(faucet_url, data=json.dumps(faucet_data))
        if response.status_code != 200:
            raise ConvexAPIError(f'faucet_request: {response.status_code} {response.text}')
        result = response.json()
        logger.debug(f'faucet_request result {result}')
        if result['address'] != remove_0x_prefix(account.address):
            raise ConvexAPIError(f'faucet_request: returned account is not correct {result["address"]}')
        return result['amount']

    def get_balance(self, address_account, account_from=None):
        value = 0
        if isinstance(address_account, str):
            address = remove_0x_prefix(address_account)
        else:
            address = remove_0x_prefix(address_account.address)

        address_from = address
        if account_from:
            if isinstance(account_from, str):
                address_from = remove_0x_prefix(account_from)
            else:
                address_from = remove_0x_prefix(account_from.address)

        result = self._transaction_query(address_from, f'(balance "{address}")')
        if 'error-code' in result:
            if result['error-code'] != 'NOBODY':
                raise ConvexAPIError(f'get balance: {result["error-code"]} {result["value"]}')
        else:
            value = result['value']
        return value

    def transfer(self, account, to_address_account, amount):
        if isinstance(to_address_account, str):
            to_address = remove_0x_prefix(to_address_account)
        else:
            to_address = remove_0x_prefix(to_address_account.address)
        if not to_address:
            raise ValueError(f'You must provide a valid to account/address ("{to_address_account}") to transfer funds too')
        result = self.send(account, f'(transfer "{to_address}" {amount})')
        return result

    def _transaction_prepare(self, address, transaction):
        prepare_url = urljoin(self._url, '/api/v1/transaction/prepare')
        data = {
            'address': remove_0x_prefix(address),
            'source': transaction,
        }
        logger.debug(f'transaction_prepare {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexAPIError(f'transaction_prepare {response.status_code} {response.text}')

        result = response.json()
        logger.debug(f'transaction_prepare repsonse {result}')
        return result

    def _transaction_submit(self, address, hash_data, signed_data):
        submit_url = urljoin(self._url, '/api/v1/transaction/submit')
        data = {
            'address': remove_0x_prefix(address),
            'hash': hash_data,
            'sig': remove_0x_prefix(signed_data)
        }
        logger.debug(f'transaction_submit {submit_url} {data}')
        response = requests.post(submit_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexAPIError(f'transaction_submit {response.status_code} {response.text}')
        result = response.json()
        logger.debug(f'transaction_submit response {result}')
        if 'error-code' in result:
            raise ConvexAPIError(f'transaction_submit error: {result["error-code"]} {result["value"]}')
        return result

    def _transaction_query(self, address, transaction):
        prepare_url = urljoin(self._url, '/api/v1/query')
        data = {
            'address': remove_0x_prefix(address),
            'source': transaction,
        }
        logger.debug(f'transaction_query {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexAPIError(f'transaction_query: {response.status_code} {response.text}')

        result = response.json()
        logger.debug(f'transaction_query repsonse {result}')
        return result
