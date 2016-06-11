from pygelf import GelfTcpHandler
import logging
import pytest
import mock


@pytest.fixture
def handler():
    return GelfTcpHandler(host='127.0.0.1', port=12000)


@pytest.yield_fixture
def send(handler):
    with mock.patch.object(handler, 'send') as mock_send:
        yield mock_send


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    yield logger
    logger.removeHandler(handler)


def test_ending_null_character(logger, send):
    logger.warning('null terminated message')
    message = send.call_args[0][0].decode('utf-8')
    assert message[-1] == '\x00'
