import socket
import pytest
import mock
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler, GelfTlsHandler, GelfHttpsHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception


SYSLOG_LEVEL_ERROR = 3
SYSLOG_LEVEL_WARNING = 4


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201),
    GelfUdpHandler(host='127.0.0.1', port=12202),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False),
    GelfHttpHandler(host='127.0.0.1', port=12203),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False),
    GelfTlsHandler(host='127.0.0.1', port=12204),
    GelfHttpsHandler(host='127.0.0.1', port=12205, validate=False),
    GelfHttpsHandler(host='localhost', port=12205, validate=True, ca_certs='tests/config/cert.pem'),
    GelfTlsHandler(host='127.0.0.1', port=12204, validate=True, ca_certs='tests/config/cert.pem'),
])
def handler(request):
    return request.param


def test_simple_message(logger):
    message = get_unique_message()
    graylog_response = log_warning(logger, message)
    assert graylog_response['message'] == message
    assert graylog_response['level'] == SYSLOG_LEVEL_WARNING
    assert 'full_message' not in graylog_response
    assert 'file' not in graylog_response
    assert 'module' not in graylog_response
    assert 'func' not in graylog_response
    assert 'logger_name' not in graylog_response
    assert 'line' not in graylog_response


def test_formatted_message(logger):
    message = get_unique_message()
    template = message + '_%s_%s'
    graylog_response = log_warning(logger, template, args=('hello', 'gelf'))
    assert graylog_response['message'] == message + '_hello_gelf'
    assert graylog_response['level'] == SYSLOG_LEVEL_WARNING
    assert 'full_message' not in graylog_response


def test_full_message(logger):
    message = get_unique_message()

    try:
        raise ValueError(message)
    except ValueError as e:
        graylog_response = log_exception(logger, message, e)
        assert graylog_response['message'] == message
        assert graylog_response['level'] == SYSLOG_LEVEL_ERROR
        assert message in graylog_response['full_message']
        assert 'Traceback (most recent call last)' in graylog_response['full_message']
        assert 'ValueError: ' in graylog_response['full_message']
        assert 'file' not in graylog_response
        assert 'module' not in graylog_response
        assert 'func' not in graylog_response
        assert 'logger_name' not in graylog_response
        assert 'line' not in graylog_response


def test_source(logger):
    original_source = socket.gethostname()
    with mock.patch('socket.gethostname', return_value='different_domain'):
        message = get_unique_message()
        graylog_response = log_warning(logger, message)
        assert graylog_response['source'] == original_source
