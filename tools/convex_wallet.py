#!/usr/bin/env python3

"""

    Script to provide convex wallet functionality

"""

import argparse
import json
import logging
import secrets

from convex_api import Account as ConvexAccount
from convex_api import ConvexAPI

DEFAULT_URL = 'https://convex.world'
COMMAND_HELP_TEXT = '''

create                      Create a new account using the provided --password. If no password auto generate one.
new                         Same as 'create' command.
info [address]              Get information about an account, you can pass the account address, or the keywords or keyfile/password of the account.
'''

logger = logging.getLogger('convex_wallet')


def auto_topup_account(convex, account, min_balance=None):
    if isinstance(account, (list, tuple)):
        for account_item in account:
            auto_topup_account(convex, account_item, min_balance)
        return
    amount = 10000000
    retry_counter = 100
    if min_balance is None:
        min_balance = amount
    balance = convex.get_balance(account)
    while balance < min_balance and retry_counter > 0:
        convex.request_funds(amount, account)
        balance = convex.get_balance(account)
        retry_counter -= 1


def load_account(args):
    account = None
    if args.keyfile and args.password:
        account = ConvexAccount.import_from_file(args.keyfile, args.password)
    elif args.keywords:
        account = ConvexAccount.import_from_mnemonic(args.keywords)
    return account

def main():

    parser = argparse.ArgumentParser(
        description='Convex Wallet',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-a',
        '--auto-topup',
        action='store_true',
        help='Auto topup account with sufficient funds. This only works for development networks. Default: False',
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Debug mode on or off. Default: False',
    )

    parser.add_argument(
        '-k',
        '--keyfile',
        help='account private key encrypted with password saved in a file'
    )

    parser.add_argument(
        '-p',
        '--password',
        help='password to access the private key enrcypted in a keyfile'
    )

    parser.add_argument(
        '-w',
        '--keywords',
        help='account private key as words'
    )

    parser.add_argument(
        '-u',
        '--url',
        default=DEFAULT_URL,
        help=f'URL of the network node. Default: {DEFAULT_URL}',
    )

    parser.add_argument(
        'command',
        help=f'Wallet commands are as follows: \r\n{COMMAND_HELP_TEXT}'
    )

    parser.add_argument(
        'command_args',
        nargs='*',
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.INFO)

    if args.command == 'create' or args.command == 'new':
        account = ConvexAccount.create_new()
        convex = ConvexAPI(args.url)
        if not convex:
            print(f'Cannot connect to the convex network at {args.url}')
            return

        if args.auto_topup:
            logger.debug('auto topup of account balance')
            auto_topup_account(convex, account)

        if args.password:
            password = args.password
        else:
            password = secrets.token_hex(32)

        values = {
            'password': password,
            'address': account.address_checksum,
            'keyfile': account.export_to_text(password),
            'keywords': account.export_to_mnemonic,
            'balance': convex.get_balance(account)
        }
        print(json.dumps(values, sort_keys=True, indent=4))
    elif args.command == 'info':
        address = None
        if len(args.command_args) > 0:
            address = args.command_args[0]

        account = load_account(args)
        if account:
            address = account.address_checksum

        if not address:
            print('you must provide account keywords/keyfile or an account address')
            return

        convex = ConvexAPI(args.url)
        if not convex:
            print(f'Cannot connect to the convex network at {args.url}')
            return

        values = convex.get_account_info(address)
        print(json.dumps(values, sort_keys=True, indent=4))

if __name__ == "__main__":
    main()
