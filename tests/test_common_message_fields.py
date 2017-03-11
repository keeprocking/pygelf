from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
from common import logger, send, log_and_decode
import pytest
import mock
import socket


ADDITIONAL_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984,
    '_id': '123'
}


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12000, **ADDITIONAL_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12000, compress=False, **ADDITIONAL_FIELDS),
    GelfTlsHandler(host='127.0.0.1', port=12000, debug=True, **ADDITIONAL_FIELDS)
])
def handler(request):
    return request.param


def test_simple_message(logger, send):
    message = log_and_decode(logger, send, 'hello gelf')
    assert message['short_message'] == 'hello gelf'
    assert 'full_message' not in message


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


def test_default_version(logger, send):
    message = log_and_decode(logger, send, 'default version')
    assert message['version'] == '1.1'


def test_source(logger, send):
    original_source = socket.getfqdn()
    with mock.patch('socket.getfqdn', return_value='different_domain'):
        message = log_and_decode(logger, send, 'do not call socket.getfqdn() each time')
        assert message['source'] == original_source


def test_debug_fields(logger, handler, send):
    message = log_and_decode(logger, send, 'hello gelf')

    debug_fields = {
        '_file': 'common.py',
        '_module': 'common',
        '_func': 'log_and_decode',
        '_logger_name': logger.name
    }

    if handler.debug:
        assert '_line' in message

    for k, v in debug_fields.items():
        if handler.debug:
            assert message[k] == v
        else:
            assert k not in message
