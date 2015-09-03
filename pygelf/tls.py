from __future__ import print_function
from pygelf.tcp import GelfTcpHandler
import ssl
import socket
import sys


class GelfTlsHandler(GelfTcpHandler):
    """
    TCP GELF logging handler with TLS support

    :param validate: if true, validate server certificate. In that case ca_certs are required.
    :param ca_certs: path to CA bundle file. For instance, on CentOS it would be '/etc/pki/tls/certs/ca-bundle.crt'
    """

    def __init__(self, validate=False, ca_certs=None, **kwargs):
        super(GelfTlsHandler, self).__init__(**kwargs)

        if validate and ca_certs is None:
            raise ValueError('CA bundle file path must be specified')

        self.ca_certs = ca_certs
        self.reqs = ssl.CERT_REQUIRED if validate else ssl.CERT_NONE

    def makeSocket(self, timeout=1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)

        try:
            wrapped_socket = ssl.wrap_socket(s, ca_certs=self.ca_certs, cert_reqs=self.reqs)
            wrapped_socket.connect((self.host, self.port))
            return wrapped_socket
        except Exception as e:
            print('SSL socket exception:', e, file=sys.stderr)
