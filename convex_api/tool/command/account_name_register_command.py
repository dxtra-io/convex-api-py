"""

    Command Account Register ..

"""

from .command_base import CommandBase


class AccountNameRegisterCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('register', sub_parser)

    def create_parser(self, sub_parser):

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

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)

        account = self.load_account(args, args.name_address, output)
        if not account:
            return

        if not self.is_address(args.address):
            output.add_error(f'{args.address} to register is not an convex account address')
            return

        register_account = convex.register_account_name(args.name, args.address, account)
        if not register_account:
            output.add_error('failet to register acccount')
            return

        output.add_line(f'registered account name {register_account.name} to address {register_account.address}')
        output.set_value('address', register_account.address)
        output.set_value('name', register_account.name)
