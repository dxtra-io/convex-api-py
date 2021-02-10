"""

    Test Convex multi thread

"""
import pytest
import secrets
from multiprocessing import (
    Process,
    Value
)

from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError
from convex_api.utils import to_address

TEST_FUNDING_AMOUNT = 8000000

def process_on_convex(convex, test_account, result_value):
    values = []
    inc_values = []
    is_sent = False
    for counter in range(0, 4):
        for index in range(secrets.randbelow(10) + 1):
            value = secrets.randbelow(1000)
            values.append(str(value))
            inc_values.append(value + 1)
            value_text = " ".join(values)
        result = convex.send(f'(map inc [{value_text}])', test_account, sequence_retry_count=100)
        assert(result)
        assert('value' in result)
        assert(result['value'] == inc_values)
    result_value.value = 1


def test_convex_api_multi_thread_send(convex_url, test_account):

    process_count = 4
    convex = ConvexAPI(convex_url)
    convex.topup_account(test_account)
    process_items = {}
    for index in range(process_count):
        result_value = Value('i', 0)
        proc = Process(target=process_on_convex, args=(convex, test_account, result_value))
        process_items[index] = {
            'process': proc,
            'result_value': result_value
        }
        proc.start()

    for index, process_item in process_items.items():
        process_item['process'].join()
        assert(process_item['result_value'].value == 1)


def process_convex_account_creation(convex, result_value):
    account = convex.create_account()
    assert(account)
    assert(account.address)
    result_value.value = 1


def test_convex_api_multi_thread_account_creation(convex_url):
    process_count = 20
    convex = ConvexAPI(convex_url)
    process_items = {}
    for index in range(process_count):
        result_value = Value('i', 0)
        proc = Process(target=process_convex_account_creation, args=(convex, result_value))
        process_items[index] = {
            'process': proc,
            'result_value': result_value
        }
        proc.start()

    for index, process_item in process_items.items():
        process_item['process'].join()
        assert(process_item['result_value'].value == 1)


def process_convex_depoly(convex, result_value):
    deploy_storage = """
(def storage-example
    (deploy
        '(do
            (def stored-data nil)
            (defn get [] stored-data)
            (defn set [x] (def stored-data x))
            (export get set)
        )
    )
)
"""
    account = convex.create_account()
    for index in range(0, 10):
        convex.topup_account(account)
        try:
            result = convex.send(deploy_storage, account)
        except ConvexAPIError as e:
            balance = convex.get_balance(account)
            print('*' * 132)
            print('failed send', e, balance)
            print('*' * 132)
            result_value.value = balance
            return
        assert(result)
        assert(result['value'])
        contract_address = to_address(result['value'])
        assert(contract_address)
    result_value.value = 1


def test_convex_api_multi_thread_deploy(convex_url):
    process_count = 10
    convex = ConvexAPI(convex_url)
    # account = convex.create_account()
    # request_amount = convex.request_funds(TEST_FUNDING_AMOUNT, account)
    process_items = {}
    for index in range(process_count):
        result_value = Value('i', 0)
        proc = Process(target=process_convex_depoly, args=(convex, result_value))
        process_items[index] = {
            'process': proc,
            'result_value': result_value
        }
        proc.start()

    for index, process_item in process_items.items():
        process_item['process'].join()
        assert(process_item['result_value'].value == 1)

