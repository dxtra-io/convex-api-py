"""

    Convex API

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
from convex_api.registry import Registry
from convex_api.utils import (
    is_address,
    to_address
)

# min amount to do a topup account
TOPUP_ACCOUNT_MIN_BALANCE = 10000000

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
        self._registry = Registry(self)

    def create_account(self, account=None, sequence_retry_count=20):
        """

        Create a new account address on the convex network.

        :param `Account` account: :class:`.Account` object that you whish to use as the signing account.
            The :class:`.Account` object contains the public/private keys to access and submit commands
            on the convex network. The address property will be changed by this method.

            If no object given, then this method will automatically create a new :class:`.Account` object.
        :type account: Account, optional


        :param sequence_retry_count: Number of retries to create the account. If too many clients are trying to
            create accounts on the same node, then we will get sequence errors.
        :type sequence_retry_count: int, optional

        :returns: A new :class:`.Account` object, or the current supplied :class:`.Account` object with a new `address` property set


        .. code-block:: python

            >>> from convex_api import ConvexAPI
            >>> convex_api = ConvexAPI('https://convex.world')
            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> print(account.address)
            >>> 42

            >>> #create a new account address, but use the same keys as `account`
            >>> new_account_address = convex_api.create_account(account=account)
            >>> print(new_account.address)
            >>> 43


        """

        if account and not isinstance(account, Account):
            raise TypeError(f'account value {account} must be a type convex_api.Account')

        # if account, then copy it
        if account:
            new_account = Account.import_from_account(account)
        else:
            # create a new account with new keys
            new_account = Account.create()

        create_account_url = urljoin(self._url, '/api/v1/createAccount')
        account_data = {
            'accountKey': remove_0x_prefix(new_account.public_key),
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
        new_account.address = to_address(result['address'])

        return new_account

    def load_account(self, name, account):
        """

        Load an account using the account name. If successfull return the account address

        """
        address = self.resolve_account_name(name)
        if address:
            new_account = Account.import_from_account(account, address=address, name=name)
            return new_account

    def register_account_name(self, name, account):
        """

        Register an account with the given address, with a name.

        """
        if account.address:
            self._registry.register(f'account.{name}', account.address, account)
            return Account.import_from_account(account, address=account.address, name=name)

    def send(self, transaction, account, language=None, sequence_retry_count=20):
        """
        Send transaction code to the block chain node.

        :param str transaction: The transaction as a string to send

        :param Account account: The account that needs to sign the message to send

        :param language: Language to use for this transaction. Defaults to LANGUAGE_LISP.
        :type language: str, optional

        :param sequence_retry_count: Number of retries to do if a SEQUENCE error occurs.
            When sending multiple send requsts on the same account, you can get SEQUENCE errors,
            This send method will automatically retry again
        :type sequence_retry_count: int, optional

        :returns: The dict returned from the result of the sent transaction.


        .. code-block:: python

            >>> from convex_api import ConvexAPI
            >>> convex_api = ConvexAPI('https://convex.world')

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()

            >>> # request some funds to do stuff
            >>> print(convex_api.request_funds(100000, account))
            100000

            >>> # submit a transaction using the new account
            >>> print(convex_api.send('(map inc [ 1 2 3 4])', account))
            {'value': [2, 3, 4, 5]}


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
        the account does not need to sign the transaction. No funds will be used when executing
        this query. For this reason you can just pass the account address, or if you want to the :class:`.Account` object.

        :param str transaction: Transaction to execute. This can only be a read only transaction.

        :param address_account: :class:`.Account` object or int address of an account to use for running this query.
        :type address_account: Account, int, str

        :param language: The type of language to use, if not provided the default language set will be used.
        :type language: str, optional

        :returns: Return the resultant query transaction


        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()

            >>> # submit a query transaction using the account address

            >>> print(convex_api.query(f'(balance {account.address})', account.address))
            {'value': 0}

            >>> # request some funds to do stuff
            >>> print(convex_api.request_funds(100000, account))
            100000
            >>> print(convex_api.query(f'(balance {account.address})', account.address))
            {'value': 100000}

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

        :param Account account: The :class:`.Account` object to receive funds too

        :returns: The amount transfered to the account


        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> # request some funds to do stuff
            >>> print(convex_api.request_funds(100000, account))
            100000

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

    def topup_account(self, account, min_balance=TOPUP_ACCOUNT_MIN_BALANCE, retry_count=8):
        """

        Topup an account from the block chain faucet, so that the balance of the account is above or equal to
        the `min_balanace`.

        :param Account account: The :class:`.Account` object to receive funds for

        :param min_balance: Minimum account balance that will allowed before a topup occurs
        :type min_balance: number, optional

        :param retry_count: The number of times the faucet will be called to get above or equal to the  `min_balance`
        :type retry_count: number, optional

        :returns: The amount transfered to the account

        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> # request some funds to do stuff
            >>> print(convex_api.topup_account(account, 100000))
            100000
            >>> # try again, but only return 0 topup amount credited
            >>> print(convex_api.topup_account(account, 100000))
            0

        """

        request_amount = min(TOPUP_ACCOUNT_MIN_BALANCE, min_balance)
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

        :param address_account: :class:`.Account` object or str address of an account to use for running this query.
        :type address_account: Account, int, str


        :returns: Returns address of the contract

        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> # find the address of a contract
            >>> print(convex_api.get_address('my_contract', account))

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

        :param address_account: Address or :class:`.Account` object to get the funds for.
        :type address_account: Account, int, str

        :param account_from: Optional :class:`.Account` object or account address to make the request.
        :type account_from: Account, int, str, optional


        :returns: Return the current balance of the address or account `address_account`

        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> # get the balance of the contract
            >>> print(convex_api.get_balance(account))
            0
            >>> print(convex_api.request_funds(100000, account))
            100000
            >>> print(convex_api.get_balance(account))
            100000

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

        :param to_address_account: Address or :class:`.Account` object to send the funds too
        :type to_address_account: Account, int, str

        :param number amount: Amount to transfer

        :param Account account: :class:`.Account` object to send the funds from

        :returns: The transfer record sent back after the transfer has been made

        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> print(convex_api.request_funds(10000000, account))
            10000000
            >>> print(convex_api.get_balance(account))
            10000000

            >>> my_account = convex_api.create_account()
            >>> # transfer some funds to my_account
            >>> print(convex_api.transfer(my_account, 100, account))
            100
            >>> print(convex_api.get_balance(my_account))
            100
            >>> print(convex_api.get_balance(account))
            9998520

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
        if result and 'value' in result:
            return result['value']
        return 0

    def get_account_info(self, address_account):
        """

        Get account information. This will only work with an account that has a balance or has had some transactions
        processed on the convex network. New accounts with no transfer or transactions will raise:

            ConvexRequestError(404, 'The Account for this Address does not exist.') error

        The returned information is dictionary of account information.

        :param address_account: :class:`.Account` object or address of an account to get current information on.
        :type address_account: Account, int, str

        :returns: dict of information, such as

        .. code-block:: python

            >>> # Create a new account with new public/priavte keys and address
            >>> account = convex_api.create_account()
            >>> # get the balance of the contract
            >>> print(convex_api.get_account_info(account))

            {'environment': {}, 'address': 1178, 'memorySize': 0, 'balance': 0,
            'isLibrary': False, 'isActor': False, 'allowance': 0,
            'sequence': 0, 'type': 'user'}




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

    def resolve_account_name(self, name):
        return self._registry.resolve_address(f'account.{name}')

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
        """

        Returns the default language to use when calling the API commands

        """
        return self._language
