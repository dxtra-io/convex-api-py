"""

    Command Account Info ..

"""

from .command_base import CommandBase


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
        info = self.resolve_to_name_address(args.name_address, output)
        if not info:
            return

        account_info = convex.get_account_info(info['address'])
        output.set_value('address', info['address'])
        if info['name']:
            output.set_value('name', info['name'])
        output.add_line_values(account_info)
        output.set_values(account_info)
