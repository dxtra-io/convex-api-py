"""

    Command 'get_ether'

"""

from .account_balance_command import AccountBalanceCommand
from .account_create_command import AccountCreateCommand
from .account_info_command import AccountInfoCommand
from .account_name_resolve_command import AccountNameResolveCommand
from .command_base import CommandBase
from .help_command import HelpCommand


class AccountCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('account', sub_parser)

    def create_parser(self, sub_parser):
        parser = sub_parser.add_parser(
            self._name,
            description='Tool tasks on accounts',
            help='Tasks to perform on accounts',

        )
        account_parser = parser.add_subparsers(
            title='Account sub command',
            description='Account sub command',
            help='Account sub command',
            dest='account_command'
        )

        self._command_list = [
            AccountBalanceCommand(account_parser),
            AccountCreateCommand(account_parser),
            AccountInfoCommand(account_parser),
            AccountNameResolveCommand(account_parser),
            HelpCommand(account_parser, self)
        ]
        return account_parser

    def execute(self, args, output):
        return self.process_sub_command(args, output, args.account_command)
