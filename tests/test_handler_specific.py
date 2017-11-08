from pygelf import GelfTlsHandler
import pytest


def test_tls_handler_creation():
    with pytest.raises(ValueError):
        GelfTlsHandler(host='127.0.0.1', port=12204, validate=True)

    with pytest.raises(ValueError):
        GelfTlsHandler(host='127.0.0.1', port=12204, keyfile='/dev/null')
