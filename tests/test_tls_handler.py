from pygelf import GelfTlsHandler
from common import logger, send
import pytest


@pytest.fixture
def handler():
    return GelfTlsHandler(host='127.0.0.1', port=12000)


def test_ending_null_character(logger, send):
    logger.warning('null terminated message')
    message = send.call_args[0][0].decode('utf-8')
    assert message[-1] == '\x00'


def test_handler_creation():
    with pytest.raises(ValueError):
        GelfTlsHandler(host='127.0.0.1', port=12001, validate=True)


def test_handler_certfile_required_for_keyfile():
    with pytest.raises(ValueError):
        GelfTlsHandler(host='127.0.0.1', port=12001, keyfile="./somefile.key")
