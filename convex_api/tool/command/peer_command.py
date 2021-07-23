"""

    Command peer

"""

from .command_base import CommandBase
from .help_command import HelpCommand
from .peer_create_command import PeerCreateCommand


class PeerCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('peer', sub_parser)

    def create_parser(self, sub_parser):
        parser = sub_parser.add_parser(
            self._name,
            description='Tool tasks on peers',
            help='Tasks to perform on peers',

        )
        peer_parser = parser.add_subparsers(
            title='Peer sub command',
            description='Peer sub command',
            help='Peer sub command',
            dest='peer_command'
        )

        self._command_list = [
            PeerCreateCommand(peer_parser),
            HelpCommand(peer_parser, self)
        ]
        return peer_parser

    def execute(self, args, output):
        return self.process_sub_command(args, output, args.peer_command)
