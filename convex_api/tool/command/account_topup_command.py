"""

    Command Account Topup ..

"""

from .command_base import CommandBase


class AccountTopupCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('topup', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='Topup an account with sufficient funds',
            help='Topup an account with sufficient funds'
        )

        parser.add_argument(
            'name_address',
            help='account address or account name'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)
        account = self.load_account(args, args.name_address, output)
        if not account:
            return

        amount = convex.topup_account(account)
        balance = convex.get_balance(account)
        output.add_line(f'topup account by {amount} to balance: {balance} for account at {account.address}')
        output.set_value('amount', amount)
        output.set_value('balance', balance)
        output.set_value('address', account.address)
        if account.name:
            output.set_value('name', account.name)
