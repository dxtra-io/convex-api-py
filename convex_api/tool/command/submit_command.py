"""

    Command Submit ..

"""
import json

from .command_base import CommandBase


class SubmitCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('submit', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='call a convex query',
            help='Call a convex query command'

        )

        parser.add_argument(
            'submit',
            help='submit to perform'
        )

        parser.add_argument(
            'name_address',
            help='account address or account name, to use for the submit'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)

        account = self.load_account(args, args.name_address, output)
        if not account:
            return

        result = convex.send(args.submit, account)
        output.add_line(json.dumps(result))
        output.set_values(result)
