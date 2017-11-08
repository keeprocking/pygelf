from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import pytest
import mock
import socket
import logging


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, debug=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, debug=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, debug=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, debug=True),
])
def handler(request):
    return request.param


def test_debug_mode(logger):
    message = get_unique_message()
    parsed_message = log_warning(logger, message)
    assert parsed_message['message'] == message
    assert parsed_message['file'] == 'helper.py'
    assert parsed_message['module'] == 'helper'
    assert parsed_message['func'] == 'log_warning'
    assert parsed_message['logger_name'] == 'test'
    assert 'line' in parsed_message
