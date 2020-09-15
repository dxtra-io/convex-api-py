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
            (def provenance [])
            (defn version [] "{CONTRACT_VERSION}")
            (defn assert-asset-id [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid asset-id"))
            )
            (defn register [asset-id]
                (assert-asset-id asset-id)
                (let [record {{:owner *caller* :timestamp *timestamp* :asset-id (blob asset-id)}}]
                    (def provenance (conj provenance record))
                    record
                )
            )
            (defn event-list [asset-id]
                (assert-asset-id asset-id)
                (mapcat (fn [record] (when (= (blob asset-id) (record :asset-id)) [record])) provenance)
            )
            (export event-list register version)
        )
    )
)
"""


def test_provenance_contract(convex, test_account):
    auto_topup_account(convex, test_account)
    print(provenance_contract)
    result = convex.send(provenance_contract, test_account)
    assert(result['value'])
    auto_topup_account(convex, test_account)
    contract_address = result['value']
    assert(contract_address)
    print(contract_address)

    asset_id = '0x' + secrets.token_hex(32)
    event_count = 4
    for index in range(0, event_count):
        result = convex.send(f'(call {contract_address} (register {asset_id}))', test_account)
        assert(result)
        record = result['value']
        assert(record['asset-id'] == asset_id)


    result = convex.query(f'(call {contract_address} (event-list {asset_id}))', test_account)
    assert(result)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == event_count)
    for event_item in event_list:
        assert(event_item['asset-id'] == asset_id)


    bad_asset_id = '0x' + secrets.token_hex(20)
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(f'(call {contract_address} (register {bad_asset_id}))', test_account)
