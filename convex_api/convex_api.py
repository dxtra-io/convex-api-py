"""


    Convex

"""

import json
import logging
from urllib.parse import urljoin
import requests


from eth_utils import remove_0x_prefix

from convex_api.exceptions import (
    ConvexAPIError,
    ConvexRequestError
)

logger = logging.getLogger(__name__)


class ConvexAPI:
    def __init__(self, url):
        self._url = url

    def send(self, transaction, account):
        """
        Send transaction code to the block chain node.

        :param str transaction: The transaction as a string to send
        :param Account account: The account that needs to sign the message to send

        :returns: The dict returned from the result of the sent transaction.

        """
        if not transaction:
            raise ValueError('You need to provide a valid transaction')
        if not isinstance(transaction, str):
            raise TypeError('The transaction must be a type str')

        hash_data = self._transaction_prepare(account.address, transaction)
        signed_data = account.sign(hash_data['hash'])
        result = self._transaction_submit(account.address, hash_data['hash'], signed_data)
        return result

    def query(self, transaction, address_account):
        """
        Run a query transaction on the block chain. Since this does not change the network state, and
        so the account does not need to sign the transaction. No funds will be used when executing
        this query.

        :param str transaction: Transaction to execute. This can only be a read only transaction.
        :param Account, str address_account: Account or str address of an account to use for running this query.

        :returns: Return the resultant query transaction

        """
        if isinstance(address_account, str):
            address = remove_0x_prefix(address_account)
        else:
            address = remove_0x_prefix(address_account.address)

        return self._transaction_query(address, transaction)

    def get_address(self, function_name, address_account):
        """

        Query the network for a contract ( function ) address. The contract must have been deployed
        by the account address provided. If not then no address will be returned

        :param str function_name: Name of the contract/function
        :param Account, str address_account: Account or str address of an account to use for running this query.

        :returns: Returns address of the contract

        """
        result = self.query(f'(address {function_name})', address_account)
        if result and 'value' in result:
            return result['value']

    def request_funds(self, amount, account):
        """
        Request funds for an account from the block chain faucet.

        :param number amount: The amount of funds to request
        :param Account account: The account to receive funds to

        :returns: The amount transfered to the account

        """
        faucet_url = urljoin(self._url, '/api/v1/faucet')
        faucet_data = {
            'address': remove_0x_prefix(account.address),
            'amount': amount
        }
        logger.debug(f'request_funds {faucet_url} {faucet_data}')
        response = requests.post(faucet_url, data=json.dumps(faucet_data))
        if response.status_code != 200:
            raise ConvexRequestError('request_funds', response.status_code, response.text)
        result = response.json()
        logger.debug(f'request_funds result {result}')
        if result['address'] != remove_0x_prefix(account.address):
            raise ValueError(f'request_funds: returned account is not correct {result["address"]}')
        return result['amount']

    def get_balance(self, address_account, account_from=None):
        """
        Get a balance of an account.
        At the moment the account needs to have a balance to get the balance of it's account or any
        other account. Event though this is using a query request.

        :param Account, str address_account: Address or Account to get the funds for.
        :param Account account_from: Optional account to use to make the request.
            This account should have a balance to make the request.

        :returns: Return the current balance of the address or account `address_account`

        """
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

        try:
            result = self._transaction_query(address_from, f'(balance "{address}")')
        except ConvexAPIError as error:
            if error.code != 'UNDECLARED':
                raise
        else:
            value = result['value']
        return value

    def transfer(self, to_address_account, amount, account):
        """
        Transfer funds from on account to another.

        :param Account, str to_address_account: Address or account to send the funds too
        :param number amonut: Amount to send
        :param Account account: Account to send the funds from

        :returns: The transfer record sent back after the transfer has been made

        """
        if isinstance(to_address_account, str):
            to_address = remove_0x_prefix(to_address_account)
        else:
            to_address = remove_0x_prefix(to_address_account.address)
        if not to_address:
            raise ValueError(f'You must provide a valid to account/address ("{to_address_account}") to transfer funds too')
        result = self.send(f'(transfer "{to_address}" {amount})', account)
        return result

    def _transaction_prepare(self, address, transaction):
        """

        """
        prepare_url = urljoin(self._url, '/api/v1/transaction/prepare')
        data = {
            'address': remove_0x_prefix(address),
            'source': transaction,
        }
        logger.debug(f'_transaction_prepare {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_prepare', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_prepare repsonse {result}')
        if 'error-code' in result:
            raise ConvexAPIError('_transaction_prepare', result['error-code'], result['value'])

        return result

    def _transaction_submit(self, address, hash_data, signed_data):
        """

        """
        submit_url = urljoin(self._url, '/api/v1/transaction/submit')
        data = {
            'address': remove_0x_prefix(address),
            'hash': hash_data,
            'sig': remove_0x_prefix(signed_data)
        }
        logger.debug(f'_transaction_submit {submit_url} {data}')
        response = requests.post(submit_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_submit', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_submit response {result}')
        if 'error-code' in result:
            raise ConvexAPIError('_transaction_submit', result['error-code'], result['value'])
        return result

    def _transaction_query(self, address, transaction):
        """

        """
        prepare_url = urljoin(self._url, '/api/v1/query')
        data = {
            'address': remove_0x_prefix(address),
            'source': transaction,
        }
        logger.debug(f'_transaction_query {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_query', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_query repsonse {result}')
        if 'error-code' in result:
            raise ConvexAPIError('_transaction_query', result['error-code'], result['value'])

        return result
