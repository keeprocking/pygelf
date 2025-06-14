import pytest
from pygelf import GelfTlsHandler, GelfHttpsHandler


def test_tls_handler_init():
    with pytest.raises(ValueError):
        GelfTlsHandler(host='localhost', port=12204, validate=True)

    with pytest.raises(ValueError):
        GelfTlsHandler(host='localhost', port=12204, keyfile='/dev/null')


def test_https_handler_init():
    with pytest.raises(ValueError):
        GelfHttpsHandler(host='localhost', port=12205, validate=True)
