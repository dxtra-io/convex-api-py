"""


    Test Convex Provenance Contract

"""

import pytest
import secrets

from tests.helpers import auto_topup_account

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError

CONTRACT_NAME='starfish-provenance'
CONTRACT_VERSION = '0.0.1'

provenance_contract = f"""
(def {CONTRACT_NAME}
    (deploy
        '(do
            (def provenance {{}})
            (defn version [] "{CONTRACT_VERSION}")
            (export version)
        )
    )
)
"""


def test_provenance_contract(convex, test_account):
    auto_topup_account(convex, test_account)
    result = convex.send(provenance_contract, test_account)
    assert(result['value'])
    auto_topup_account(convex, test_account)
    contract_address = result['value']
    assert(contract_address)
    print(contract_address)
