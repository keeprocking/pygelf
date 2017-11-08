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
    GelfUdpHandler(host='127.0.0.1', port=12202, **STATIC_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, **STATIC_FIELDS),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, **STATIC_FIELDS),
])
def handler(request):
    return request.param


def test_static_fields(logger):
    message = get_unique_message()
    parsed_message = log_warning(logger, message, fields=['ozzy', 'van_halen'])
    assert parsed_message['message'] == message
    assert parsed_message['ozzy'] == 'diary of a madman'
    assert parsed_message['van_halen'] == 1984
    assert parsed_message['_id'] != 42
    assert 'id' not in parsed_message
