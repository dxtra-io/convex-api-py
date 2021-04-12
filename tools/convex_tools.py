#!/usr/bin/env python3

"""

    Script to provide convex wallet functionality

"""

import argparse
import logging


from convex_api.tool.command.account_command import AccountCommand
from convex_api.tool.command.command_base import DEFAULT_CONVEX_URL
from convex_api.tool.output import Output


logger = logging.getLogger('convex_tools')


def main():

    parser = argparse.ArgumentParser(
        description='Convex Tools',
        formatter_class=argparse.RawTextHelpFormatter
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
        '-d',
        '--debug',
        action='store_true',
        help='Debug mode on or off. Default: False',
    )

    parser.add_argument(
        '-j',
        '--json',
        action='store_true',
        help='Output data as JSON values'
    )

    parser.add_argument(
        '-u',
        '--url',
        default=DEFAULT_CONVEX_URL,
        help=f'URL of the network node. Default: {DEFAULT_CONVEX_URL}',
    )

    command_parser = parser.add_subparsers(
        title='Convex commands',
        description='Command values',
        help='Convex commands',
        dest='command'
    )

    command_list = [
        AccountCommand(command_parser),
    ]

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    output = Output()

    is_found = False
    for command_item in command_list:
        if command_item.is_command(args.command):
            command_item.execute(args, output)
            is_found = True
            break

    if not is_found:
        parser.print_help()

    output.printout(args.json)

    """
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
    """


if __name__ == "__main__":
    main()
