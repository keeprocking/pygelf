import logging
import pytest
import mock
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler, GelfTlsHandler, GelfHttpsHandler
from tests.helper import logger, get_unique_message, log_exception


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201),
    GelfUdpHandler(host='127.0.0.1', port=12202),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False),
    GelfHttpHandler(host='127.0.0.1', port=12203),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False),
    GelfTlsHandler(host='127.0.0.1', port=12204),
    GelfHttpsHandler(host='127.0.0.1', port=12205, validate=False),
    GelfTlsHandler(host='127.0.0.1', port=12204, validate=True, ca_certs='tests/config/cert.pem'),
    GelfHttpsHandler(host='localhost', port=12205, validate=True, ca_certs='tests/config/cert.pem'),
])
def handler(request):
    return request.param


def fake_handle(self, record):
    self.format(record)
    record.exc_info = None
    self.emit(record)


def test_full_message(logger):
    message = get_unique_message()

    with mock.patch.object(logging.Handler, 'handle', new=fake_handle):
        try:
            raise ValueError(message)
        except ValueError as e:
            graylog_response = log_exception(logger, message, e)
            assert message in graylog_response['full_message']
            assert 'Traceback (most recent call last)' in graylog_response['full_message']
            assert 'ValueError: ' in graylog_response['full_message']
