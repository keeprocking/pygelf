from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
from common import log_and_decode
import logging
import json
import pytest
import mock


@pytest.mark.parametrize('handler,version', [
    (GelfTcpHandler(host='127.0.0.1', port=12000, version='10.7'), '10.7'),
    (GelfUdpHandler(host='127.0.0.1', port=12000, compress=False, version='11.5'), '11.5'),
    (GelfTlsHandler(host='127.0.0.1', port=12000, version='12.3'), '12.3')
])
def test_custom_version(handler, version):
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    with mock.patch.object(handler, 'send') as send:
        message = log_and_decode(logger, send, 'custom version')
        assert message['version'] == version
    logger.removeHandler(handler)
