"""

    Test Account Command Tool

"""
from unittest.mock import Mock

from convex_api.tool.command.account_balance_command import AccountBalanceCommand
from convex_api.tool.command.account_create_command import AccountCreateCommand
from convex_api.tool.command.account_info_command import AccountInfoCommand
from convex_api.tool.command.account_name_resolve_command import AccountNameResolveCommand
from convex_api.tool.output import Output



def test_account_create_command(convex_url):
    args = Mock()

    args.url = convex_url
    args.password = 'test_password'
    args.keyfile = None
    args.keywords = None
    args.name = None

    command = AccountCreateCommand()
    output = Output()
    command.execute(args, output)
    print(output.values)
    assert(output.values['keyfile'])
    assert(output.values['address'])
    assert(output.values['password'])



def test_account_balance_command(convex_url, test_account):
    args = Mock()

    args.url = convex_url
    args.name_address = test_account.address

    command = AccountBalanceCommand()
    output = Output()
    command.execute(args, output)
    assert(output.values['balance'])


    args.url = convex_url
    args.name_address = test_account.name

    command = AccountBalanceCommand()
    output = Output()
    command.execute(args, output)
    assert(output.values['balance'])


def test_account_info_command(convex_url, test_account):
    args = Mock()

    args.url = convex_url
    args.name_address = test_account.address

    command = AccountInfoCommand()
    output = Output()
    command.execute(args, output)
    assert(output.values['balance'])
    assert(output.values['memorySize'])
    assert(output.values['sequence'])
    assert(output.values['type'])


    args.url = convex_url
    args.name_address = test_account.name

    command = AccountInfoCommand()
    output = Output()
    command.execute(args, output)
    assert(output.values['balance'])
    assert(output.values['memorySize'])
    assert(output.values['sequence'])
    assert(output.values['type'])


def test_account_name_resolve_command(convex_url, test_account):
    args = Mock()

    args.url = convex_url
    args.name = test_account.name

    command = AccountNameResolveCommand()
    output = Output()
    command.execute(args, output)
    assert(output.values['address'] == test_account.address)
