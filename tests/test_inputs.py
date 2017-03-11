from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from common import logger
import uuid
import requests
import time
import os
import pytest


SKIP_TEST = os.environ.get('TEST_INPUTS') is None


ADDITIONAL_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984
}
API_URL = 'http://127.0.0.1:9000/api/search/universal/relative?query={0}&range=5&fields=' \
    + '%2C'.join(('message', 'van_halen', 'ozzy', 'func', 'file', 'line', 'module', 'logger_name'))


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, debug=True, **ADDITIONAL_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True, **ADDITIONAL_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True, compress=False, **ADDITIONAL_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, debug=True, **ADDITIONAL_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, debug=True, compress=False, **ADDITIONAL_FIELDS),
])
def handler(request):
    return request.param


@pytest.mark.skipif(SKIP_TEST, reason="Missing TEST_INPUTS env variable")
def test_input(logger):
    unique_message = str(uuid.uuid4())

    logger.warning(unique_message)
    time.sleep(3)

    url = API_URL.format(unique_message)
    api_response = requests.get(url, auth=('admin', 'admin'), headers={'accept': 'application/json'})

    assert api_response.status_code == 200

    messages = api_response.json()['messages']
    assert len(messages) == 1

    message = messages[0]['message']
    assert message['message'] == unique_message
    assert message['ozzy'] == 'diary of a madman'
    assert message['van_halen'] == 1984
    assert message['func'] == 'test_input'
    assert message['file'] == 'test_inputs.py'
    assert message['module'] == 'test_inputs'
    assert message['logger_name'] == logger.name
    assert 'line' in message
