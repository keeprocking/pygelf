from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import pytest
import mock
import socket
import logging


SYSLOG_LEVEL_WARNING = 4


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201),
    GelfUdpHandler(host='127.0.0.1', port=12202),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False),
    GelfHttpHandler(host='127.0.0.1', port=12203),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False),
])
def handler(request):
    return request.param


def test_simple_message(logger):
    message = get_unique_message()
    parsed_message = log_warning(logger, message)
    assert parsed_message['message'] == message
    assert parsed_message['level'] == SYSLOG_LEVEL_WARNING
    assert 'full_message' not in parsed_message


def test_formatted_message(logger):
    message = get_unique_message()
    template = message + '_%s_%s'
    parsed_message = log_warning(logger, template, args=('hello', 'gelf'))
    assert parsed_message['message'] == message + '_hello_gelf'
    assert parsed_message['level'] == SYSLOG_LEVEL_WARNING
    assert 'full_message' not in parsed_message


def test_source(logger):
    original_source = socket.getfqdn()
    with mock.patch('socket.getfqdn', return_value='different_domain'):
        message = get_unique_message()
        parsed_message = log_warning(logger, message)
        assert parsed_message['source'] == original_source
