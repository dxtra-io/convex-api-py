"""

    Command Account Name Resolve ..

"""

from .command_base import CommandBase


class AccountNameResolveCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('resolve', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='Get an address from an account name',
            help='Get an address from an account name'

        )

        parser.add_argument(
            'name',
            help='account name to resolve'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)
        address = convex.resolve_account_name(args.name)
        if address:
            output.add_line(f'address: {address}')
        else:
            output.add_line('not found')
        output.set_value('address', address)
        output.set_value('name', args.name)
