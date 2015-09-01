from __future__ import print_function
from pygelf.tcp import GelfTcpHandler
import ssl
import socket
import sys


class GelfTlsHandler(GelfTcpHandler):

    def __init__(self, cert, **kwargs):
        super(GelfTlsHandler, self).__init__(**kwargs)
        self.cert = cert

    def makeSocket(self, timeout=1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)

        try:
            wrapped_socket = ssl.wrap_socket(s, ca_certs=self.cert, cert_reqs=ssl.CERT_REQUIRED)
            wrapped_socket.connect((self.host, self.port))
            return wrapped_socket
        except Exception as e:
            print('SSL socket exception:', e, file=sys.stderr)
