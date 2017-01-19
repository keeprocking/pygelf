from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
import logging
import json
import pytest
import mock


@pytest.yield_fixture
def send(extra_fields_handler):
    with mock.patch.object(extra_fields_handler, 'send') as mock_send:
        yield mock_send


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12000, include_extra_fields=True),
    GelfUdpHandler(host='127.0.0.1', port=12000, compress=False, include_extra_fields=True),
    GelfTlsHandler(host='127.0.0.1', port=12000, include_extra_fields=True)
])
def extra_fields_handler(request):
    return request.param


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.ozzy = 'diary of a madman'
        record.van_halen = 1984
        record.id = 123
        return True


@pytest.yield_fixture
def extra_fields_logger(extra_fields_handler):
    extra_fields_logger = logging.getLogger('test')
    context_filter = ContextFilter()
    extra_fields_logger.addFilter(context_filter)
    extra_fields_logger.addHandler(extra_fields_handler)
    yield extra_fields_logger
    extra_fields_logger.removeHandler(extra_fields_handler)
    extra_fields_logger.removeFilter(context_filter)


def log_and_decode(_logger, _send, text, *args):
    _logger.exception(text) if isinstance(text, Exception) else _logger.warning(text, *args)
    message = _send.call_args[0][0].replace(b'\x00', b'').decode('utf-8')
    return json.loads(message)


def test_extra_fields(extra_fields_logger, send):
    message = log_and_decode(extra_fields_logger, send, 'hello gelf')
    assert '_id' not in message  # same fields were set thru filter

    expected = [
        ('_ozzy', 'diary of a madman'),
        ('_van_halen', 1984)
    ]

    for (k, v) in expected:
        if k != '_id':
            assert message[k] == v

