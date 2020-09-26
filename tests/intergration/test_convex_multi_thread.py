"""

    Test Convex multi thread

"""
import pytest
import secrets
from multiprocessing import Process

from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError

from tests.helpers import auto_topup_account

def process_on_convex(convex, test_account):
    values = []
    inc_values = []
    is_sent = False
    for index in range(secrets.randbelow(10) + 1):
        value = secrets.randbelow(1000)
        values.append(str(value))
        inc_values.append(value + 1)
        value_text = " ".join(values)
    while (not is_sent):
        try:
            result = convex.send(f'(map inc [{value_text}])', test_account)
        except ConvexAPIError as error:
            print('retrying again...')
            is_sent = False
        else:
            is_sent = True
    assert 'id' in result
    assert 'value' in result
    assert(result['value'] == inc_values)


def test_convex_api_multi_thread(convex_url, test_account):

    process_count = 4
    convex = ConvexAPI(convex_url)
    auto_topup_account(convex, test_account)
    process_list = []
    for index in range(process_count):
        proc = Process(target=process_on_convex, args=(convex, test_account))
        proc.start()
        process_list.append(proc)

    for proc in process_list:
        proc.join()
