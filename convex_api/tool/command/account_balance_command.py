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
        info = self.resolve_to_name_address(args.name_address, output)
        if not info:
            return

        balance = convex.get_balance(info['address'])
        output.add_line(f'balance: {balance} for account at {info["address"]}')
        output.set_value('balance', balance)
        output.set_value('address', info['address'])
        if info['name']:
            output.set_value('name', info['name'])
