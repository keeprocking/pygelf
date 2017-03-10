from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
from common import send, log_and_decode
import logging
import pytest


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.ozzy = 'diary of a madman'
        record.van_halen = 1984
        record.id = 123
        return True


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12000, include_extra_fields=True),
    GelfUdpHandler(host='127.0.0.1', port=12000, compress=False, include_extra_fields=True),
    GelfTlsHandler(host='127.0.0.1', port=12000, include_extra_fields=True)
])
def handler(request):
    return request.param


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    context_filter = ContextFilter()
    logger.addFilter(context_filter)
    logger.addHandler(handler)
    yield logger
    logger.removeHandler(handler)
    logger.removeFilter(context_filter)


def test_extra_fields(logger, send):
    message = log_and_decode(logger, send, 'hello gelf')

    assert '_id' not in message

    expected = [
        ('_ozzy', 'diary of a madman'),
        ('_van_halen', 1984)
    ]

    for k, v in expected:
        assert message[k] == v

