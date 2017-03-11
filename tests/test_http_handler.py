from pygelf import GelfHttpHandler
from common import logger
import json
import pytest
import mock

try:
    import httplib
except ImportError:
    import http.client as httplib


ADDITIONAL_FIELDS = {
    '_ozzy': 'diary of a madman',
    '_van_halen': 1984
}


@pytest.fixture
def handler():
    return GelfHttpHandler(host='127.0.0.1', port=12000, compress=False, **ADDITIONAL_FIELDS)


@pytest.yield_fixture
def http_request():
    with mock.patch.object(httplib.HTTPConnection, 'request') as mock_http_request:
        yield mock_http_request


def log_and_decode(_logger, _http_request, text, *args):
    _logger.exception(text) if isinstance(text, Exception) else _logger.warning(text, *args)
    message = _http_request.call_args[0][2].decode('utf-8')
    return json.loads(message)


def test_simple_message(logger, http_request):
    message = log_and_decode(logger, http_request, 'hello gelf')
    assert message['short_message'] == 'hello gelf'
    assert 'full_message' not in message


def test_full_message(logger, http_request):
    try:
        raise Exception('something went wrong')
    except Exception as e:
        message = log_and_decode(logger, http_request, e)
        assert message['short_message'] == 'something went wrong'
        assert 'Traceback (most recent call last)' in message['full_message']
        assert 'Exception: something went wrong' in message['full_message']


def test_formatted_message(logger, http_request):
    message = log_and_decode(logger, http_request, '%s %s', 'hello', 'gelf')
    assert message['short_message'] == 'hello gelf'


def test_additional_fields(logger, http_request):
    message = log_and_decode(logger, http_request, 'hello gelf')
    assert message['short_message'] == 'hello gelf'
    assert message['_ozzy'] == 'diary of a madman'
    assert message['_van_halen'] == 1984
