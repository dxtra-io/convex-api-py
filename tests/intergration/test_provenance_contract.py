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
            (defn assert-address [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
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
            (defn event-owner [owner-id]
                (assert-address owner-id)
                (mapcat (fn [record] (when (= (address owner-id) (record :owner)) [record])) provenance)
            )
            (defn event-timestamp [time-from time-to]
                (mapcat
                    (fn [record]
                        (when
                            (and
                                (<= time-from (record :timestamp))
                                (>= time-to (record :timestamp))
                            )
                        [record] )
                    )
                provenance)
            )
            (export event-list event-owner event-timestamp register version)
        )
    )
)
"""


provenance_contract_address = None
test_event_list = None

@pytest.fixture
def contract_address(convex, test_account):
    global provenance_contract_address
    auto_topup_account(convex, test_account, 50000000)
    if provenance_contract_address is None:
        print(provenance_contract)
        result = convex.send(provenance_contract, test_account)
        assert(result['value'])
        auto_topup_account(convex, test_account)
        provenance_contract_address = result['value']
    return provenance_contract_address

@pytest.fixture
def register_test_list(pytestconfig, convex, test_account, other_account, contract_address):
    global test_event_list
    if not test_event_list:
        test_event_list = []
        event_count = 10
        auto_topup_account(convex, test_account)

        register_account = other_account
        for index in range(0, event_count):
            if index % 2 == 0:
                asset_id = '0x' + secrets.token_hex(32)
                if register_account.address == test_account.address:
                    register_account = other_account
                else:
                    register_account = test_account
            result = convex.send(f'(call {contract_address} (register {asset_id}))', register_account)
            assert(result)
            record = result['value']
            assert(record['asset-id'] == asset_id)
            test_event_list.append(record)
    return test_event_list

def test_contract_version(convex, test_account, contract_address):
    command = f'(call {contract_address} (version))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == CONTRACT_VERSION)

def test_provenance_contract_register(register_test_list):
    assert(register_test_list)

def test_provenance_contract_event_list(convex, test_account, contract_address, register_test_list):
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    result = convex.query(f'(call {contract_address} (event-list {record["asset-id"]}))', test_account)
    assert(result)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == 2)
    event_item = event_list[0]
    assert(event_item['asset-id'] == record['asset-id'])
    assert(event_item['owner'] == record['owner'])

def test_provenance_contract_event_owner_list(convex, test_account, contract_address, register_test_list):
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    owner_count = 0
    for item in register_test_list:
        if item['owner'] == record['owner']:
            owner_count += 1
    result = convex.query(f'(call {contract_address} (event-owner {record["owner"]}))', test_account)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == owner_count)
    for event_item in event_list:
        assert(event_item['owner'] == record["owner"])

def test_provenance_contract_event_timestamp_list(convex, test_account, contract_address, register_test_list):
    record_from = register_test_list[2]
    record_to = register_test_list[len(register_test_list) - 2]
    timestamp_from = record_from['timestamp']
    timestamp_to = record_to['timestamp']
    result = convex.query(f'(call {contract_address} (event-timestamp {timestamp_from} {timestamp_to}))', test_account)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == len(register_test_list) - 3)
    for event_item in event_list:
        assert(event_item['timestamp'] >= timestamp_from and event_item['timestamp'] <= timestamp_to)

def test_provenance_contract_event_timestamp_item(convex, test_account, contract_address, register_test_list):
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    timestamp = record['timestamp']
    result = convex.query(f'(call {contract_address} (event-timestamp {timestamp} {timestamp}))', test_account)
    event_list = result['value']
    assert(len(event_list) == 1)
    event_item = event_list[0]
    assert(event_item['timestamp'] == timestamp)

def test_bad_asset_id(convex, test_account, contract_address):
    bad_asset_id = '0x' + secrets.token_hex(20)
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(f'(call {contract_address} (register {bad_asset_id}))', test_account)


