from pygelf import GelfUdpHandler
import logging
import json
import zlib
import pytest
import mock


@pytest.fixture
def handler():
    return GelfUdpHandler(host='127.0.0.1', port=12000, version='2.2', compress=False, chunk_size=10)


@pytest.yield_fixture
def send(handler):
    with mock.patch.object(handler, 'send') as mock_send:
        yield mock_send


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    yield logger


def log_and_decode(_logger, _send, text, compress=False):
    _logger.warning(text)
    message = _send.call_args[0][0]
    message = zlib.decompress(message).decode('utf-8') if compress else message.decode('utf-8')
    return json.loads(message)


def test_version(logger, send):
    message = log_and_decode(logger, send, 'custom version')
    assert message['version'] == '2.2'
