from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import pytest
import mock
import socket
import logging


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, _ozzy='diary of a madman', _van_halen=1984, _id=42),
    GelfUdpHandler(host='127.0.0.1', port=12202, _ozzy='diary of a madman', _van_halen=1984, _id=42),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, _ozzy='diary of a madman', _van_halen=1984, _id=42),
    GelfHttpHandler(host='127.0.0.1', port=12203, _ozzy='diary of a madman', _van_halen=1984, _id=42),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, _ozzy='diary of a madman', _van_halen=1984, _id=42),
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
