"""


    Convex

"""

import json
import logging
import re
import secrets
import time

from urllib.parse import urljoin

import requests
from eth_utils import remove_0x_prefix

from convex_api.account import Account

from convex_api.exceptions import (
    ConvexAPIError,
    ConvexRequestError
)
from convex_api.utils import (
    is_address,
    to_address
)


logger = logging.getLogger(__name__)


class ConvexAPI:

    LANGUAGE_LISP = 'convex-lisp'
    LANGUAGE_SCRYPT = 'convex-scrypt'
    LANGUAGE_ALLOWED = [LANGUAGE_LISP, LANGUAGE_SCRYPT]

    def __init__(self, url, language=LANGUAGE_LISP):
        self._url = url

        if language not in ConvexAPI.LANGUAGE_ALLOWED:
            raise ValueError(f'Invalid language: {language}')
        self._language = language

    def create_account(self, account=None, sequence_retry_count=20):
        if account is None:
            account = Account.create()
        create_account_url = urljoin(self._url, '/api/v1/createAccount')
        account_data = {
            'accountKey': remove_0x_prefix(account.public_key),
        }

        logger.debug(f'create_account {create_account_url} {account_data}')

        max_sleep_time_seconds = 1
        while sequence_retry_count >= 0:
            response = requests.post(create_account_url, data=json.dumps(account_data))
            if response.status_code == 200:
                result = response.json()
                break
            elif response.status_code == 400:
                if not re.search(':SEQUENCE ', response.text):
                    raise ConvexRequestError('create_account', response.status_code, response.text)

                if sequence_retry_count == 0:
                    raise ConvexRequestError('create_account', response.status_code, response.text)
                sequence_retry_count -= 1
                # now sleep < 1 second for at least 1 millisecond
                sleep_time = secrets.randbelow(round(max_sleep_time_seconds * 1000)) / 1000
                time.sleep(sleep_time + 1)
            else:
                raise ConvexRequestError('create_account', response.status_code, response.text)
        logger.debug(f'create_account result {result}')
        account.address = to_address(result['address'])
        return account

    def send(self, transaction, account, language=None, sequence_retry_count=20):
        """
        Send transaction code to the block chain node.

        :param str transaction: The transaction as a string to send
        :param Account account: The account that needs to sign the message to send
        :param str language: Language to use for this transaction. Defaults to LANGUAGE_LISP.
        :param int sequence_retry_count: Number of retries to do if a SEQUENCE error occurs.
            When sending multiple send requsts on the same account, you can get SEQUENCE errors,
            This send method will automatically retry again

        :returns: The dict returned from the result of the sent transaction.

        """
        if not transaction:
            raise ValueError('You need to provide a valid transaction')
        if not isinstance(transaction, str):
            raise TypeError('The transaction must be a type str')

        result = None
        max_sleep_time_seconds = 1
        while sequence_retry_count >= 0:
            try:
                hash_data = self._transaction_prepare(account.address, transaction, language=language)
                signed_data = account.sign(hash_data['hash'])
                result = self._transaction_submit(account.address, account.public_key_checksum, hash_data['hash'], signed_data)
            except ConvexAPIError as error:
                if error.code == 'SEQUENCE':
                    if sequence_retry_count == 0:
                        raise
                    sequence_retry_count -= 1
                    # now sleep < 1 second for at least 1 millisecond
                    sleep_time = secrets.randbelow(round(max_sleep_time_seconds * 1000)) / 1000
                    time.sleep(sleep_time + 1)
                else:
                    raise
            else:
                break
        return result

    def query(self, transaction, address_account, language=None):
        """
        Run a query transaction on the block chain. Since this does not change the network state, and
        so the account does not need to sign the transaction. No funds will be used when executing
        this query.

        :param str transaction: Transaction to execute. This can only be a read only transaction.
        :param Account, str address_account: Account or str address of an account to use for running this query.

        :returns: Return the resultant query transaction

        """
        if is_address(address_account):
            address = to_address(address_account)
        else:
            address = address_account.address

        return self._transaction_query(address, transaction, language)

    def request_funds(self, amount, account):
        """
        Request funds for an account from the block chain faucet.

        :param number amount: The amount of funds to request
        :param Account account: The account to receive funds to

        :returns: The amount transfered to the account

        """
        faucet_url = urljoin(self._url, '/api/v1/faucet')
        faucet_data = {
            'address': account.address,
            'amount': amount
        }
        logger.debug(f'request_funds {faucet_url} {faucet_data}')
        response = requests.post(faucet_url, data=json.dumps(faucet_data))
        if response.status_code != 200:
            raise ConvexRequestError('request_funds', response.status_code, response.text)
        result = response.json()
        logger.debug(f'request_funds result {result}')
        if result['address'] != account.address:
            raise ValueError(f'request_funds: returned account is not correct {result["address"]}')
        return result['amount']

    def topup_account(self, account, min_balance=1000000, retry_count=8):
        """
        Topup an account from the block chain faucet, so that the balance of the account is above or equal to
        the `min_balanace`.

        :param number amount: The amount of funds to request
        :param Account account: The account to receive funds for
        :param number min_balance: Minimum account balance that will allowed before a topup occurs
        :Param number retry_count: The number of times the faucet will be called to get above or equal to the  `min_balance`

        :returns: The amount transfered to the account

        """

        request_amount = min(10000000, min_balance)
        retry_count = min(5, retry_count)
        transfer_amount = 0
        while min_balance > self.get_balance(account) and retry_count > 0:
            transfer_amount += self.request_funds(request_amount, account)
            retry_count -= 1
        return transfer_amount

    def get_address(self, function_name, address_account):
        """

        Query the network for a contract ( function ) address. The contract must have been deployed
        by the account address provided. If not then no address will be returned

        :param str function_name: Name of the contract/function
        :param Account, str address_account: Account or str address of an account to use for running this query.

        :returns: Returns address of the contract

        """

        line = f'(address {function_name})'
        if self._language == ConvexAPI.LANGUAGE_SCRYPT:
            line = f'address({function_name})'
        result = self.query(line, address_account)
        if result and 'value' in result:
            return to_address(result['value'])

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
        if is_address(address_account):
            address = to_address(address_account)
        else:
            address = address_account.address

        address_from = address
        if account_from:
            if is_address(account_from):
                address_from = to_address(account_from)
            else:
                address_from = account_from.address
        line = f'(balance {address})'
        if self._language == ConvexAPI.LANGUAGE_SCRYPT:
            line = f'balance({address})'
        try:

            result = self._transaction_query(address_from, line)
        except ConvexAPIError as error:
            if error.code != 'NOBODY':
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
        if is_address(to_address_account):
            transfer_to_address = to_address(to_address_account)
        else:
            transfer_to_address = to_address_account.address
        if not to_address:
            raise ValueError(f'You must provide a valid to account/address ({transfer_to_address}) to transfer funds too')

        line = f'(transfer {transfer_to_address} {amount})'
        if self._language == ConvexAPI.LANGUAGE_SCRYPT:
            line = f'transfer({transfer_to_address}, {amount})'

        result = self.send(line, account)
        return result

    def get_account_info(self, address_account):
        """
        Get account information. This will only work with an account that has a balance or has had some transactions
        processed on the convex network. New accounts with no transfer or transactions will raise:

            ConvexRequestError(404, 'The Account for this Address does not exist.') error

        The returned information is dictionary of account information.

        :param Account, str address_account: Account or str address of an account to get current information on.
        :returns: dict of information, such as

        .. code-block: json
            {
                "address": "42",
                "isLibrary": false,
                "isActor": false,
                "memorySize": 75,
                "allowance": 10000000,
                "type": "user",
                "balance": 10000000000,
                "sequence": 0,
            }


        """
        if is_address(address_account):
            address = to_address(address_account)
        else:
            address = address_account.address

        account_url = urljoin(self._url, f'/api/v1/accounts/{address}')
        logger.debug(f'get_account_info {account_url}')

        response = requests.get(account_url)
        if response.status_code != 200:
            raise ConvexRequestError('get_account_info', response.status_code, response.text)

        result = response.json()
        logger.debug(f'get_account_info repsonse {result}')
        return result

    def _transaction_prepare(self, address, transaction, language=None, sequence_number=None):
        """

        """
        if language is None:
            language = self._language
        prepare_url = urljoin(self._url, '/api/v1/transaction/prepare')
        data = {
            'address': address,
            'lang': language,
            'source': transaction,
        }
        if sequence_number:
            data['sequence'] = sequence_number
        logger.debug(f'_transaction_prepare {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_prepare', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_prepare repsonse {result}')
        if 'errorCode' in result:
            raise ConvexAPIError('_transaction_prepare', result['errorCode'], result['value'])

        return result

    def _transaction_submit(self, address, public_key, hash_data, signed_data):
        """

        """
        submit_url = urljoin(self._url, '/api/v1/transaction/submit')
        data = {
            'address': to_address(address),
            'accountKey': remove_0x_prefix(public_key),
            'hash': hash_data,
            'sig': remove_0x_prefix(signed_data)
        }
        logger.debug(f'_transaction_submit {submit_url} {data}')
        response = requests.post(submit_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_submit', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_submit response {result}')
        if 'errorCode' in result:
            raise ConvexAPIError('_transaction_submit', result['errorCode'], result['value'])
        return result

    def _transaction_query(self, address, transaction, language=None):
        """

        """
        if language is None:
            language = self._language

        prepare_url = urljoin(self._url, '/api/v1/query')
        data = {
            'address': address,
            'lang': language,
            'source': transaction,
        }
        logger.debug(f'_transaction_query {prepare_url} {data}')
        response = requests.post(prepare_url, data=json.dumps(data))
        if response.status_code != 200:
            raise ConvexRequestError('_transaction_query', response.status_code, response.text)

        result = response.json()
        logger.debug(f'_transaction_query repsonse {result}')
        if 'errorCode' in result:
            raise ConvexAPIError('_transaction_query', result['errorCode'], result['value'])
        return result

    @property
    def language(self):
        return self._language
