"""

    Command Account Balance ..

"""

from .command_base import CommandBase

DEFAULT_AMOUNT = 10


class AccountBalanceCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('balance', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='Get balance from an account address or name',
            help='Get balance of an account'

        )

        parser.add_argument(
            'name_address',
            help='account address or account name'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)
        address = None
        name = None
        if args.name_address:
            address = convex.resolve_account_name(args.name_address)
            name = args.name_address

        if not address:
            address = args.name_address

        if not self.is_address(address):
            output.add_error(f'{address} is not an convex account address')
            return

        balance = convex.get_balance(address)
        output.add_line(f'balance: {balance} for account at {address}')
        output.set_value('balance', balance)
        output.set_value('address', address)
        if name:
            output.set_value('name', name)
