from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import pytest
import mock
import socket
import logging


STATIC_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984,
    '_id': 42
}


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, **STATIC_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, **STATIC_FIELDS),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, **STATIC_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, **STATIC_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, **STATIC_FIELDS),
    GelfTcpHandler(host='127.0.0.1', port=12201, static_fields=STATIC_FIELDS, _ozzy='billie jean'),
    GelfUdpHandler(host='127.0.0.1', port=12202, static_fields=STATIC_FIELDS, _ozzy='billie jean'),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, static_fields=STATIC_FIELDS, _ozzy='billie jean'),
    GelfHttpHandler(host='127.0.0.1', port=12203, static_fields=STATIC_FIELDS, _ozzy='billie jean'),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, static_fields=STATIC_FIELDS, _ozzy='billie jean'),
])
def handler(request):
    return request.param


def test_static_fields(logger):
    message = get_unique_message()
    graylog_response = log_warning(logger, message, fields=['ozzy', 'van_halen'])
    assert graylog_response['message'] == message
    assert graylog_response['ozzy'] == 'diary of a madman'
    assert graylog_response['van_halen'] == 1984
    assert graylog_response['_id'] != 42
    assert 'id' not in graylog_response
