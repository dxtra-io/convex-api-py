"""

    Account class for convex api


"""
import secrets

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from eth_utils import (
    remove_0x_prefix,
    to_bytes,
    to_hex
)

from mnemonic import Mnemonic

from convex_api.utils import (
    to_address,
    to_public_key_checksum
)


class Account:

    def __init__(self, private_key, address=None):
        """

        Create a new account with a private key as a Ed25519PrivateKey. It is better to use
        one of the following static methods to create an Account object:

            * :meth:`.create`
            * :meth:`import_from_bytes`
            * :meth:`import_from_file`
            * :meth:`import_from_mnemonic`
            * :meth:`import_from_text`

        :param Ed25519PrivateKey private_key: The public/private key as an Ed25519PrivateKey object

        :param int address: address of the account


        The Convex account class, contains the public/private keys and possibly an address.

        You can create a new account object, it will only have it's public/private keys but does not have a valid account address.
        To obtain a new account address, you need to call the :py:meth:`.ConvexAPI.create_account` with the new account object.

        This is so that you can use the same public/private keys for multiple convex accounts.

        Once you have your new account you need to save the public/private keys using the `export..` methods and also you
        need to save the account address.

        To re-use the account again, you can import the keys and set the account address using one of the `import..` methods.

        **Note**
        For security reasons all of the keys, and text returned by the accounts are only truncated ending with a **`...`**

        .. code-block:: python

            >>> # import convex-api
            >>> from convex_api import ConvexAPI

            >>> # setup the network connection
            >>> convex_api = ConvexAPI('https://convex.world')

            >>> # create a new account and address
            >>> account = convex_api.create_account()

            >>> # export the private key to a file
            >>> account.export_to_file('/tmp/my_account.pem', 'my secret password')

            >>> # save the address for later
            >>> my_address = account.address

            >>> # ----

            >>> # now import the account and address for later use
            >>> reload_account = Account.import_from_file('/tmp/my_account.pem', 'my secret password', my_address)

        """
        self._private_key = private_key
        self._public_key = private_key.public_key()
        self._address = None
        if address is not None:
            self._address = to_address(address)

    def copy(self):
        """

        Copies the account public/private keys and returns a new account object with the same address

        :returns: A new account object.
        :rtype: Account

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()
            >>> new_account = account.copy()
            >>> print(new_account.is_address)
            True

        """
        temp_secret = secrets.token_hex(64)
        pem_text = self.export_to_text(temp_secret)
        return Account.import_from_text(pem_text, temp_secret, self.address)

    def sign(self, hash_text):
        """

        Sign a hash text using the private key.

        :param str hash_text: Hex string of the hash to sign

        :returns: Hex string of the signed text

        .. code-block:: python

            >>> # create an account with no address
            >>> account = Account.create()
            >>> # sign a given hash
            >>> sig = account.sign('7e2f1062f5fc51ed65a28b5945b49425aa42df6b7e67107efec357794096e05e')
            >>> print(sig)
            '5d41b964c63d1087ad66e58f4f9d3fe2b7bd0560b..'

        """
        hash_data = to_bytes(hexstr=hash_text)
        signed_hash_bytes = self._private_key.sign(hash_data)
        return to_hex(signed_hash_bytes)

    def export_to_text(self, password):
        """

        Export the private key to an encrypted PEM string.

        :param str password: Password to encrypt the private key value

        :returns: The private key as a PEM formated encrypted string

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # export the private key for later use
            >>> print(account.export_to_text('secret password'))
            -----BEGIN ENCRYPTED PRIVATE KEY-----
            MIGbMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAhKG+LC3hJoJQICCAAw
            DAYIKoZIhvcNAgkFAD ...


        """
        if isinstance(password, str):
            password = password.encode()
        private_data = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return private_data.decode()

    @property
    def export_to_mnemonic(self):
        """

        Export the private key as a mnemonic words. You must keep this secret since the private key can be
        recreated using the words.

        :returns: mnemonic word list of the private key

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # export the private key for later use
            >>> print(account.export_to_mnemonic())
            grief stuff resemble dry frozen exercise ...

        """
        mnemonic = Mnemonic('english')
        return mnemonic.to_mnemonic(self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        ))

    def export_to_file(self, filename, password):
        """

        Export the private key to a file. This uses `export_to_text` to export as a string.
        Then saves this in a file.

        :param str filename: Filename to create with the PEM string

        :param str password: Password to use to encypt the private key

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # export the private key to a file
            >>> account.export_to_file('my_account.pem', 'secret password')


        """
        with open(filename, 'w') as fp:
            fp.write(self.export_to_text(password))

    def __str__(self):
        return f'Account {self.address}'

    @property
    def is_address(self):
        """

        Return true if the address for this account object is set

        :returns: True if this object has a valid address

        """
        return self._address is not None

    @property
    def address(self):
        """

        :returns: the network account address
        :rtype: int

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()
            >>> print(account.address)
            42

        """
        return self._address

    @address.setter
    def address(self, value):
        """

        Sets the network address of this account

        :param value: Address to use for this account
        :type value: str, int

        .. code-block:: python

            >>> # import the account keys
            >>> account = Account.import_from_mnemonic('my private key words ..')

            >>> # set the address that was given to us when we created the account on the network
            >>> account.address = 42

        """
        self._address = to_address(value)

    @property
    def public_key_bytes(self):
        """

        Return the public key address of the account in the byte format

        :returns: Address in bytes
        :rtype: byte

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # show the public key as bytes
            >>> print(account.public_key_bytes)
            b'6\\xd8\\xc5\\xc4\\r\\xbe-\\x1b\\x011\\xac\\xf4\\x1c8..

        """
        public_key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return public_key_bytes

    @property
    def public_key(self):
        """

        Return the public key of the account in the format '0x....'

        :returns: public_key with leading '0x'
        :rtype: str

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # show the public key as a hex string
            >>> print(account.public_key)
            0x36d8c5c40dbe2d1b0131acf41c38b9d37ebe04d85...

        """
        return to_hex(self.public_key_bytes)

    @property
    def public_key_api(self):
        """

        Return the public key of the account without the leading '0x'

        :returns: public_key without the leading '0x'
        :rtype: str

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # show the public key as a hex string with the leading '0x' removed
            >>> print(account.public_key_api)
            36d8c5c40dbe2d1b0131acf41c38b9d37ebe04d85...


        """
        return remove_0x_prefix(self.public_key)

    @property
    def public_key_checksum(self):
        """

        Return the public key of the account with checksum upper/lower case characters

        :returns: str public_key in checksum format

        .. code-block:: python

            >>> # create an account with the network
            >>> account = convex_api.create_account()

            >>> # show the public key as a hex string in checksum format
            >>> print(account.public_key_checksum)
            0x36D8c5C40dbE2D1b0131ACf41c38b9D37eBe04D85...

        """

        return to_public_key_checksum(self.public_key)

    @staticmethod
    def create():
        """

        Create a new account with a random key and an empty address.

        :returns: New Account object
        :rtype: Account

        .. code-block:: python

            >>> # create an account with no address
            >>> account = Account.create()
            >> account.is_address
            False

            >>> # create two accounts with the same public/private keys
            >>> account_1 = convex_api.create_account(account)
            >>> print(account_1.address)
            42

            >>> account_2 = convex_api.create_account(account)
            >>> print(account_2.address)
            43



        """
        return Account(Ed25519PrivateKey.generate())

    @staticmethod
    def import_from_bytes(value, address=None):
        """

        Import an account from a private key in bytes.

        :param address: address of the account
        :type address: str, int, optional

        :returns: Account object with the private/public key
        :rtype: Account

        .. code-block:: python

            >>> # create an account object from a raw private key
            >>> account = Account.import_from_bytes(0x0x973f69bcd654b26475917072...)


        """
        return Account(Ed25519PrivateKey.from_private_bytes(value), address=address)

    @staticmethod
    def import_from_text(text, password, address=None):
        """

        Import an accout from an encrypted PEM string.

        :param str text: PAM text string with the encrypted key text

        :param str password: password to decrypt the private key

        :param address: address of the account
        :type address: str, int, optional

        :returns: Account object with the public/private key
        :rtype: Account

        .. code-block:: python

            >>> # create an account object from a enrcypted pem text
            >>> pem_text = '''-----BEGIN ENCRYPTED PRIVATE KEY-----
                MIGbMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAi3qm1zgjCO5gICCAAw
                DAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEENjvj1n...
            '''
            >>> account = Account.import_from_text(pem_text, 'my secret password')


        """
        if isinstance(password, str):
            password = password.encode()
        if isinstance(text, str):
            text = text.encode()

        private_key = serialization.load_pem_private_key(text, password, backend=default_backend())
        if private_key:
            return Account(private_key, address=address)

    @staticmethod
    def import_from_mnemonic(words, address=None):
        """

        Creates a new account object using a list of words. These words contain the private key and must be kept secret.

        :param str words: List of mnemonic words to read

        :param address: address of the account
        :type address: str, int, optional

        :returns: Account object with the public/private key
        :rtype: Account

        .. code-block:: python

            >>> # create an account object from a mnemonic word list with the account address 42
            >>> # the address in this example has been created by using the method `ConvexAPI.create_account`

            >>> account = Account.import_from_text('my word list that is the private key ..', 42)

        """

        mnemonic = Mnemonic('english')
        value = mnemonic.to_entropy(words)
        return Account(Ed25519PrivateKey.from_private_bytes(value), address=address)

    @staticmethod
    def import_from_file(filename, password, address=None):
        """

        Load the encrypted private key from file. The file is saved in PEM format encrypted with a password

        :param str filename: Filename to read

        :param str password: password to decrypt the private key

        :param address: address of the account
        :type address: str, int, optional

        :returns: Account with the private/public key
        :rtype: Account

        .. code-block:: python

            >>> # create an account object from a enrcypted pem saved in a file
            >>> account = Account.import_from_file(my_account_key.pem, 'my secret password')


        """
        with open(filename, 'r') as fp:
            return Account.import_from_text(fp.read(), password, address=address)
