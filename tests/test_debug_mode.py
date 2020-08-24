import pytest
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler, GelfTlsHandler, GelfHttpsHandler
from tests.helper import logger, get_unique_message, log_warning


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, debug=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, debug=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, debug=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, debug=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, debug=True),
    GelfTlsHandler(host='127.0.0.1', port=12204, debug=True),
    GelfTlsHandler(host='127.0.0.1', port=12204, debug=True, validate=True, ca_certs='tests/config/cert.pem'),
    GelfHttpsHandler(host='localhost', port=12205, debug=True, validate=True, ca_certs='tests/config/cert.pem')

])
def handler(request):
    return request.param


def test_debug_mode(logger):
    message = get_unique_message()
    graylog_response = log_warning(logger, message)
    assert graylog_response['message'] == message
    assert graylog_response['file'] == 'helper.py'
    assert graylog_response['module'] == 'helper'
    assert graylog_response['func'] == 'log_warning'
    assert graylog_response['logger_name'] == 'test'
    assert 'line' in graylog_response
