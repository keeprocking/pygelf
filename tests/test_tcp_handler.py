from pygelf import GelfTcpHandler
import logging
import json
import pytest
import mock


@pytest.fixture
def handler():
    return GelfTcpHandler(host='127.0.0.1', port=12000, debug=True)


@pytest.yield_fixture
def send(handler):
    with mock.patch.object(handler, 'send') as mock_send:
        yield mock_send


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    yield logger


def decode_send_result(send_result):
    assert send_result.call_args is not None

    message = send_result.call_args[0][0].decode('utf-8')
    assert message[-1] == '\x00'

    return json.loads(message[:-1])
