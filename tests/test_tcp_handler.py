from pygelf import GelfTcpHandler
from common import logger, send
import pytest


@pytest.fixture
def handler():
    return GelfTcpHandler(host='127.0.0.1', port=12000)


def test_ending_null_character(logger, send):
    logger.warning('null terminated message')
    message = send.call_args[0][0].decode('utf-8')
    assert message[-1] == '\x00'
