import pytest
import mock
import logging
import json


class FakeQueueHandler(logging.Handler):
    def __init__(self, handler):
        self.handler = handler
        logging.Handler.__init__(self)

    def emit(self, record):
        # This is what python3's QueueHandler does to a logging record
        # before it puts it on a Queue for a QueueListener to pick up
        self.format(record)
        record.msg = record.message
        record.args = None
        record.exc_info = None
        self.handler.handle(record)


@pytest.yield_fixture
def send(handler):
    with mock.patch.object(handler, 'send') as mock_send:
        yield mock_send


@pytest.yield_fixture(params=[True, False])
def logger(request, handler):
    logger = logging.getLogger('test')
    if request.param:
        # Should be queued
        handler = FakeQueueHandler(handler)
    logger.addHandler(handler)
    yield logger
    logger.removeHandler(handler)


def log_and_decode(_logger, _send, text, *args):
    _logger.exception(text) if isinstance(text, Exception) else _logger.warning(text, *args)
    message = _send.call_args[0][0].replace(b'\x00', b'').decode('utf-8')
    return json.loads(message)
