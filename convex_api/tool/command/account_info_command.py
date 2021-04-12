"""

    Command Account Info ..

"""

from .command_base import CommandBase

DEFAULT_AMOUNT = 10


class AccountInfoCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('info', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='Get account information',
            help='Get account information'

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

        info = convex.get_account_info(address)
        output.set_value('address', address)
        if name:
            output.set_value('name', name)
        output.add_line_values(info)
        output.set_values(info)
