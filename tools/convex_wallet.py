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
from convex_api.utils import is_address


DEFAULT_URL = 'https://convex.world'

COMMAND_HELP_TEXT = '''

create                      Create a new account using the provided --password. If no password auto generate one.
new                         Same as 'create' account command.
info [address]              Get information about an account, you can pass the account address, or the options <keywords> or <keyfile>/<password> of the account.

'''         # noqa: E501

logger = logging.getLogger('convex_wallet')


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
        nargs='?',
        help='account private key encrypted with password saved in a file'
    )

    parser.add_argument(
        '-p',
        '--password',
        nargs='?',
        help='password to access the private key enrcypted in a keyfile'
    )

    parser.add_argument(
        '-w',
        '--keywords',
        nargs='?',
        help='account private key as words'
    )

    parser.add_argument(
        '-n',
        '--name',
        nargs='?',
        help='account name to register'
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
    convex = ConvexAPI(args.url)
    if not convex:
        print(f'Cannot connect to the convex network at {args.url}')
        return

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.INFO)

    if args.command == 'create' or args.command == 'new':
        import_account = load_account(args)
        account = convex.create_account(account=import_account)

        if args.auto_topup:
            logger.debug('auto topup of account balance')
            convex.topup_account(account)

        if args.name:
            convex.topup_account(account)
            account = convex.register_account_name(args.name, account)

        if args.password:
            password = args.password
        else:
            password = secrets.token_hex(32)

        values = {
            'password': password,
            'address': account.address,
            'keyfile': account.export_to_text(password),
            'keywords': account.export_to_mnemonic,
            'balance': convex.get_balance(account)
        }
        if account.name:
            values['name'] = account.name

        print(json.dumps(values, sort_keys=True, indent=4))
    elif args.command == 'info':
        address = None
        if len(args.command_args) > 0:
            if is_address(args.command_args[0]):
                address = args.command_args[0]
            else:
                name = args.command_args[0]
                address = convex.resolve_account_name(name)
        if not address:
            print('cannot find account address using name or address provided')
            return
        values = convex.get_account_info(address)
        print(json.dumps(values, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
