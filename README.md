# Convex API

![](https://github.com/Convex-Dev/convex-api-py/workflows/testing/badge.svg)

[Documentation](https://convex-dev.github.io/convex-api-py)

### Quick Start

First you need to download the Convex-API-py package from the python package index PyPi.

    pip install convex-api

You can now access the convex network, and get a balance from an existing account on the network by doing the following:

    >>> from convex_api import ConvexAPI
    >>> convex_api = ConvexAPI('https://convex.world')
    >>> convex_api.get_balance(9)
    99396961137042

You can create a new emtpy account, with now balance:

    >>> account = convex.create_account()
    >>> account.address
    809

You can request some funds to the new account and then get the account information:

    >>> convex_api.request_funds(1000000, account)
    1000000
    >>> convex.get_account_info(account)
    {'environment': {}, 'address': 809, 'is_library': False, 'is_actor': False, 'memory_size': 42, 'balance': 1000000, 'allowance': 0, 'sequence': 0, 'type': 'user'}


You can export the accounts private key encoded as PKCS8 encrypt the key with a password:

    >>> account.export_to_text('secret')
    '-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIGbMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAiMY42UY4PXHAICCAAw\nDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEJpwDMicGbGj2iSJesktIVYEQBsp\nKMTAHzvUyw8jZRr8WSrmxH7938sjma8XWI6lgd9jwTZzcGamog7p3zatw0Wp+jFK\nKruWAZmIqhBZ/2ezDv8=\n-----END ENCRYPTED PRIVATE KEY-----\n'

    >>> account.address
    809

To re-use your account again you need to import the encrypted private key and set the correct account address

    >>> from convex_api import Account
    >>> account = Account.import_from_file('my_key.dat', 'secret', address=809)

To create a new address with the same account keys in your new or imported account object, you can do:

    >>> new_account = convex.create_account(account)
    >>> account.address
    809
    >>> new_account.address
    934

To submit a transaction, use ConvexAPI.send(). This will cost a small about of juice, and reduce your balance

    >>> convex_api.request_funds(1000000, account)
    1000000
    >>> convex_api.send('(map inc [1 2 3 4])', account)
    {'value': [2, 3, 4, 5]}
    >>> convex_api.get_balance(account)
    996360

To query a transaction, this is free and can be performed out by any valid account address.
Get the balance of the new account:

    >>> convex_api.query(f'(balance {account.address})', account)
    {'value': 996360}

    # this is the same as above
    >>> convex_api.query(f'(balance {account.address})', account.address)
    {'value': 996360}

    # get the balance using one of the standard account addresses (#1)
    >>> convex_api.query(f'(balance {account.address})', 1)
    {'value': 996360}

