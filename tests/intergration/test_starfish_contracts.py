"""


    Test Convex Contracts for Starfish

"""

import pytest
import secrets

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError

CONTRACT_NAME='starfish-did-registry'
CONTRACT_VERSION = '0.0.4'

did_registry_contract = f"""
(def starfish-did-registry
    (deploy
        '(do
            (def registry {{}})
            (def creator *caller*)
            (defn version [] "{CONTRACT_VERSION}")
            (defn get-register [did] (get registry did) )
            (defn set-register [did owner-address ddo]
                (let [register-record {{:owner owner-address :ddo ddo}}]
                    (def registry (assoc registry did register-record))
                )
            )
            (defn delete-register [did] (def registry (dissoc registry did)) )
            (defn assert-owner [did]
                (when-not (owner? did) (fail "NOT-OWNER" "not owner"))
            )
            (defn assert-address [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
            )
            (defn assert-did [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid DID"))
            )
            (defn resolve? [did]
                (assert-did did)
                (boolean (get-register did))
            )
            (defn resolve [did]
                (assert-did did)
                (when-let [register-record (get-register did)] (register-record :ddo))
            )
            (defn owner [did]
                (assert-did did)
                (when-let [register-record (get-register did)] (register-record :owner))
            )
            (defn owner? [did] (= (owner did) *caller*) )
            (defn register [did ddo]
                (assert-did did)
                (when (resolve? did) (assert-owner did))
                (set-register did *caller* ddo)
                did
            )
            (defn unregister [did]
                (when (resolve? did)
                    (assert-owner did)
                    (delete-register did)
                    did
                )
            )
            (defn transfer [did to-account]
                (when (resolve? did)
                    (assert-owner did)
                    (assert-address to-account)
                    (set-register did (address to-account) (resolve did))
                    [did (address to-account)]
                )
            )
            (defn dump [] registry )
            (defn owner-list [the-owner]
                (assert-address the-owner)
                (mapcat (fn [k v] (when (= (address the-owner) (get v :owner)) [k])) (keys registry) (values registry))
            )
            (export dump resolve resolve? register unregister owner owner? owner-list transfer version)
        )
    )
)
"""

deploy_single_contract_did_registry = """
# single contract per did, deployed contract is the didid
(def starfish-did-registry
    (deploy
        '(do
            (def store-owner *caller*)
            (def store-ddo nil)
            (defn resolve [] store-ddo)
            (defn register[x]
                (assert (owner?))
                (def store-ddo x)
            )
            (defn owner? [] (= store-owner *caller*))
            (defn owner [] store-owner)
            (export resolve register owner? owner)
        )
    )
)
"""

did_register_contract_address = None

def auto_topup_account(convex, account, min_balance=None):
    amount = 10000000
    retry_counter = 100
    if min_balance is None:
        min_balance = amount
    balance = convex.get_balance(account)
    while balance < min_balance and retry_counter > 0:
        request_amount = convex.request_funds(amount, account)
        balance = convex.get_balance(account)
        retry_counter -= 1


@pytest.fixture()
def convex(convex_url):
    api = ConvexAPI(convex_url)
    return api


@pytest.fixture()
def contract_address(convex, test_account):
    global did_register_contract_address
    auto_topup_account(convex, test_account, 50000000)
    if did_register_contract_address is None:
        result = convex.send(did_registry_contract, test_account)
        assert(result['value'])
        auto_topup_account(convex, test_account)
        did_register_contract_address = result['value']
    return did_register_contract_address


@pytest.fixture()
def other_account(convex):
    account = Account.create_new()
    auto_topup_account(convex, account)
    return account

def test_contract_version(convex, test_account, contract_address):
    command = f'(call {contract_address} (version))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == CONTRACT_VERSION)

def test_contract_did_register_assert_did(convex, test_account, contract_address):

    auto_topup_account(convex, test_account)

    did_bad = secrets.token_hex(20)
    did_valid = secrets.token_hex(32)
    ddo = 'test - ddo'
    command = f'(call {contract_address} (register "{did_bad}" "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register "" "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register 42 "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register 0x{did_valid} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == f'0x{did_valid}')


def test_contract_did_register_resolve(convex, test_account, other_account, contract_address):

    auto_topup_account(convex, test_account)

    did = f'0x{secrets.token_hex(32)}'
    ddo = 'test - ddo'


    # call register

    command = f'(call {contract_address} (register {did} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to ddo

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call resolve did to ddo on other account

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, other_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])

    # call owner? on owner other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(not result['value'])

    # call resolve unknown
    bad_did = f'0x{secrets.token_hex(32)}'
    command = f'(call {contract_address} (resolve {bad_did}))'
    result = convex.query(command, test_account)
    assert(result['value'] == '')


    new_ddo = 'new - ddo'
    # call register - update

    command = f'(call {contract_address} (register {did} "{new_ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)


    # call register - update from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, other_account)


    # call resolve did to new_ddo

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == new_ddo)


    # call unregister fail - from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (unregister {did}))'
        result = convex.send(command, other_account)


    # call unregister

    command = f'(call {contract_address} (unregister {did}))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to empty

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'] == '')


    # call unregister - unknown did

    command = f'(call {contract_address} (unregister {bad_did}))'
    result = convex.send(command, test_account)
    assert(result['value'] == '')



def test_contract_ddo_transfer(convex, test_account, other_account):
    # register and transfer

    auto_topup_account(convex, test_account)

    contract_address = convex.get_address('starfish-did-registry', test_account)
    assert(contract_address)

    did = f'0x{secrets.token_hex(32)}'
    ddo = 'test - ddo'

    command = f'(call {contract_address} (register {did} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])

    # call owner? on other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(not result['value'])


    command = f'(call {contract_address} (transfer {did} {other_account.address_checksum}))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'][0] == did)

    #check ownership to different accounts

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(not result['value'])

    # call owner? on other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(result['value'])

    # call unregister fail - from test_account (old owner)

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (unregister {did}))'
        result = convex.send(command, test_account)


    # call unregister from other_account ( new owner )

    command = f'(call {contract_address} (unregister {did}))'
    result = convex.send(command, other_account)
    assert(result['value'])
    assert(result['value'] == did)

def test_contract_ddo_bulk_register(convex, test_account):
    contract_address = convex.get_address('starfish-did-registry', test_account)
    assert(contract_address)

    for index in range(0, 2):
        auto_topup_account(convex, test_account, 40000000)
        did = f'0x{secrets.token_hex(32)}'
#        ddo = secrets.token_hex(51200)
        ddo = secrets.token_hex(1024)

        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, test_account)
        assert(result['value'])
        assert(result['value'] == did)

def test_contract_ddo_dump(convex, test_account, other_account):

    contract_address = convex.get_address('starfish-did-registry', test_account)
    assert(contract_address)

    did_list = []
    for index in range(0, 4):
        auto_topup_account(convex, test_account)
        did = f'0x{secrets.token_hex(32)}'
        did_list.append(did)
#        ddo = secrets.token_hex(51200)
        ddo = f'ddo test - {index}'

        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, test_account)
        assert(result['value'])
        assert(result['value'] == did)


    command = f'(call {contract_address} (dump))'
    result = convex.query(command, test_account)
    assert(result['value'])
    for did in did_list:
        assert(did in list(result['value'].keys()))


    command = f'(call {contract_address} (dump))'
    result = convex.query(command, other_account)
    assert(result['value'])
    for did in did_list:
        assert(did in list(result['value'].keys()))

    command = f'(call {contract_address} (owner-list "{test_account.address_api}"))'
    result = convex.query(command, test_account)
    assert(result['value'])
    for did in did_list:
        assert(did in result['value'])
