"""

    Command Query ..

"""
import json

from .command_base import CommandBase


class QueryCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('query', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='call a convex query',
            help='Call a convex query command'

        )

        parser.add_argument(
            'query',
            help='query to perform'
        )

        parser.add_argument(
            'name_address',
            nargs='?',
            help='account address or account name. Defaults: Address #1'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)

        if args.name_address:
            info = self.resolve_to_name_address(args.name_address, output)
            if not info:
                return
            address = info['address']

        address = 1
        result = convex.query(args.query, address)
        output.add_line(json.dumps(result))
        output.set_values(result)
