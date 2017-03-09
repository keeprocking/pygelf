from pygelf import GelfTcpHandler, GelfUdpHandler
from common import logger
import uuid
import requests
import time
import pytest


ADDITIONAL_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984
}
API_URL = 'http://127.0.0.1:9000/api/search/universal/relative?query={}&range=5&fields=message%2Cvan_halen%2Cozzy'


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, debug=True, **ADDITIONAL_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True, **ADDITIONAL_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True, compress=True, **ADDITIONAL_FIELDS),
])
def handler(request):
    return request.param

@pytest.mark.inputs
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

    for k, v in ADDITIONAL_FIELDS.items():
        assert message[k[1:]] == v
