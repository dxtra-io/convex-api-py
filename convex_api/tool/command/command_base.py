"""

    Command Base Class

"""

from abc import (
    ABC,
    abstractmethod
)

from convex_api import ConvexAPI
from convex_api.utils import is_address


DEFAULT_CONVEX_URL = 'https://convex.world'


class CommandBase(ABC):
    def __init__(self, name, sub_parser=None):
        self._name = name
        self._sub_parser = sub_parser
        if sub_parser:
            self.create_parser(sub_parser)

    def is_command(self, name):
        return self._name == name

    def load_convex(self, url, default_url=None):
        if url is None:
            url = default_url
        if url is None:
            url = DEFAULT_CONVEX_URL
        return ConvexAPI(url)

    def process_sub_command(self, args, output, command):
        is_found = False
        for command_item in self._command_list:
            if command_item.is_command(command):
                command_item.execute(args, output)
                is_found = True
                break

        if not is_found:
            self.print_help()

    def print_help(self):
        self._sub_parser.choices[self._name].print_help()

    def is_address(self, value):
        return is_address(value)

    @abstractmethod
    def create_parser(self, sub_parser):
        pass

    @abstractmethod
    def execute(self, args, output):
        pass

    @property
    def name(self) -> str:
        return self._name
