"""

Command Account Utils


"""
import logging

from convex_api import Account


logger = logging.getLogger('convex_tools')


def load_account(args):
    account = None
    if args.keyfile and args.password:
        logger.debug(f'importing keyfile {args.keyfile}')
        account = Account.import_from_file(args.keyfile, args.password)
    elif args.keywords:
        logger.debug('importing key from mnemonic')
        account = Account.import_from_mnemonic(args.keywords)
    return account
