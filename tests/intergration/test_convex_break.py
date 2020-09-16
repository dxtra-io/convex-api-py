"""


    Test Convex Breaking

"""

import pytest
import secrets

from tests.helpers import auto_topup_account

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError


def test_convex_recursion(convex, test_account):
    chain_length = 4
    address_list = []
    for index in range(0, chain_length):
        contract = f"""
(def chain-{index}
    (deploy
        '(do
            (def stored-data nil)
            (def chain-address nil)
            (defn get [] (call chain-address (get)))
            (defn set [x] (if chain-address (call chain-address(set x)) (def stored-data x)) )
            (defn set-chain-address [x] (def chain-address x))
            (export get set set-chain-address)
        )
    )
)
"""
        auto_topup_account(convex, test_account)
        result = convex.send(contract, test_account)
        address_list.append(result['value'])
    for index in range(0, chain_length):
        next_index = index + 1
        if next_index == chain_length:
            next_index = 0
        call_address = address_list[next_index]
        result = convex.send(f'(call chain-{index} (set-chain-address {call_address}))', test_account)
        test_number = secrets.randbelow(1000)
        if index == chain_length - 1:
            with pytest.raises(ConvexAPIError, match='DEPTH'):
                result = convex.send(f'(call chain-{index} (set {test_number}))', test_account)
        else:
            result = convex.send(f'(call chain-0 (set {test_number}))', test_account)
            assert(result)
            assert(result['value'] == test_number)
    with pytest.raises(ConvexAPIError, match='DEPTH'):
        convex.query('(call chain-0 (get))', test_account)
