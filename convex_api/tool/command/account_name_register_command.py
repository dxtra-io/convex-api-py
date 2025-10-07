"""

    Command Account Register ..

"""

from argparse import Namespace
from typing import (
    Literal,
    Union
)
from convex_api import (
    Account,
    KeyPair
)
from convex_api.tool.command.argparse_typing import (
    BaseArgs,
    SubParsersAction
)
from convex_api.tool.output import Output

from .command_base import CommandBase


class AccountNameRegisterArgs(BaseArgs):
    command: Literal['account']
    account_command: Literal['register']
    name_address: Union[str, int]
    name: str
    address: Union[str, int]
    register_key: str
    register_address: Union[str, int]


class AccountNameRegisterCommand(CommandBase):

    def __init__(self, sub_parser: SubParsersAction | None = None):
        self._command_list = []
        super().__init__('register', sub_parser)

    def create_parser(self, sub_parser: SubParsersAction):

        parser = sub_parser.add_parser(
            self._name,
            description='Register an account name',
            help='Register an account name'
        )

        parser.add_argument(
            'name_address',
            help='account address or account name to pay and the owner of the registration'
        )

        parser.add_argument(
            'name',
            help='account account name to register'
        )

        parser.add_argument(
            'address',
            help='account address to register'
        )

        parser.add_argument(
            'register_key',
            help='registry account private key as a mnemonic'
        )

        parser.add_argument(
            'register_address',
            help='registry account address'
        )

        return parser

    def execute(self, args: Namespace, output: Output):
        typed_args = AccountNameRegisterArgs.model_validate(vars(args))
        convex = self.load_convex(typed_args.url)

        account = self.load_account(typed_args, typed_args.name_address, output)
        if not account:
            return

        if not self.is_address(typed_args.address):
            output.add_error(f'{typed_args.address} to register is not an convex account address')
            return

        register_key_pair = KeyPair.import_from_mnemonic(typed_args.register_key)
        register_account = Account(register_key_pair, typed_args.register_address)
        if not register_account:
            output.add_error('failed to loadd  the register account')
            return

        reg_account = convex.register_account_name(typed_args.name, account, register_account)

        if not reg_account:
            output.add_error('failed to register the account address')
            return

        output.add_line(f'registered account name {reg_account.name} to address {reg_account.address}')
        output.set_value('address', reg_account.address)
        if reg_account.name:
            output.set_value('name', reg_account.name)
