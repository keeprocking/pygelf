from pygelf import GelfTcpHandler
import logging
import json
import pytest
import mock


ADDITIONAL_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984,
    '_id': '123'
}


@pytest.fixture
def handler():
    return GelfTcpHandler(host='127.0.0.1', port=12000, debug=True, **ADDITIONAL_FIELDS)


@pytest.yield_fixture
def send(handler):
    with mock.patch.object(handler, 'send') as mock_send:
        yield mock_send


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    yield logger


def log_and_decode(_logger, _send, text, *args):
    _logger.exception(text) if isinstance(text, Exception) else _logger.warning(text, *args)
    message = _send.call_args[0][0][:-1].decode('utf-8')
    return json.loads(message)


def test_null_character(logger, send):
    logger.warning('null termination')
    message = send.call_args[0][0].decode('utf-8')
    assert message[-1] == '\x00'


def test_simple_message(logger, send):
    message = log_and_decode(logger, send, 'hello gelf')
    assert message['short_message'] == 'hello gelf'
    assert message['full_message'] is None


def test_full_message(logger, send):
    try:
        raise Exception('something went wrong')
    except Exception as e:
        message = log_and_decode(logger, send, e)
        assert message['short_message'] == 'something went wrong'
        assert 'Traceback (most recent call last)' in message['full_message']
        assert 'Exception: something went wrong' in message['full_message']


def test_formatted_message(logger, send):
    message = log_and_decode(logger, send, '%s %s', 'hello', 'gelf')
    assert message['short_message'] == 'hello gelf'


def test_additional_fields(logger, send):
    message = log_and_decode(logger, send, 'hello gelf')
    assert '_id' not in message
    for k, v in ADDITIONAL_FIELDS.items():
        if k != '_id':
            assert message[k] == v
