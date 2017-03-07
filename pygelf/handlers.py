from logging.handlers import SocketHandler, DatagramHandler
from logging import Handler
from pygelf import gelf
import ssl
import socket
try:
    import httplib
except:
    import http.client as httplib


class BaseHandler(object):
    def __init__(self, debug=False, version='1.1', include_extra_fields=False, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over TCP.

        :param debug: include debug fields, e.g. line number, or not
        :param include_extra_fields: include non-default fields from record to message, or not
        :param kwargs: additional fields that will be included in the log message, e.g. application name.
                       Each additional field should start with underscore, e.g. _app_name
        """

        self.debug = debug
        self.version = version
        self.additional_fields = kwargs
        self.include_extra_fields = include_extra_fields
        self.additional_fields.pop('_id', None)
        self.domain = socket.getfqdn()


class GelfTcpHandler(BaseHandler, SocketHandler):

    def __init__(self, host, port, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over TCP.

        :param host: GELF TCP input host
        :param port: GELF TCP input port
        """

        SocketHandler.__init__(self, host, port)
        BaseHandler.__init__(self, **kwargs)

    def makePickle(self, record):
        message = gelf.make(record, self.domain, self.debug, self.version, self.additional_fields, self.include_extra_fields)
        packed = gelf.pack(message)

        """ if you send the message over tcp, it should always be null terminated or the input will reject it """
        return packed + b'\x00'


class GelfUdpHandler(BaseHandler, DatagramHandler):

    def __init__(self, host, port, compress=True, chunk_size=1300, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over UDP.
        If message length exceeds chunk_size, the message splits into multiple chunks.
        The number of chunks must be less than 128.

        :param host: GELF UDP input host
        :param port: GELF UDP input port
        :param compress: compress message before send it to the server or not
        :param chunk_size: length of a chunk, should be less than the MTU (maximum transmission unit)
        """

        DatagramHandler.__init__(self, host, port)
        BaseHandler.__init__(self, **kwargs)

        self.compress = compress
        self.chunk_size = chunk_size

    def send(self, s):
        if len(s) <= self.chunk_size:
            DatagramHandler.send(self, s)
        else:
            chunks = gelf.split(s, self.chunk_size)
            for chunk in chunks:
                DatagramHandler.send(self, chunk)

    def makePickle(self, record):
        message = gelf.make(record, self.domain, self.debug, self.version, self.additional_fields, self.include_extra_fields)
        packed = gelf.pack(message, self.compress)
        return packed


class GelfTlsHandler(GelfTcpHandler):

    def __init__(self, validate=False, ca_certs=None, certfile=None, keyfile=None, **kwargs):
        """
        TCP GELF logging handler with TLS support

        :param validate: if true, validate server certificate. In that case ca_certs are required.
        :param ca_certs: path to CA bundle file. For instance, on CentOS it would be '/etc/pki/tls/certs/ca-bundle.crt'
        :param certfile: path to the certificate file that is used to identify ourselves to the server.
        :param keyfile: path to the private key. If the private key is stored with the certificate this parameter can be ignored.
        """

        if validate and ca_certs is None:
            raise ValueError('CA bundle file path must be specified')

        if keyfile is not None and certfile is None:
            raise ValueError('certfile must be specified')

        GelfTcpHandler.__init__(self, **kwargs)

        self.ca_certs = ca_certs
        self.reqs = ssl.CERT_REQUIRED if validate else ssl.CERT_NONE

        self.certfile = certfile
        # Assume that if no keyfile was supplied, the private key it's in the certfile
        self.keyfile = keyfile or certfile

    def makeSocket(self, timeout=1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)

        wrapped_socket = ssl.wrap_socket(s, keyfile=self.keyfile, certfile=self.certfile,
                                         ca_certs=self.ca_certs, cert_reqs=self.reqs)
        wrapped_socket.connect((self.host, self.port))

        return wrapped_socket


class GelfHttpHandler(BaseHandler, Handler):

    def __init__(self, host, port, url='/gelf', timeout=5, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over HTTP.
        If request returns a non-202 status, an exception is raised and handled by self.handleError

        :param host:  GELF HTTP input IP
        :param port:  GELF HTTP input Port
        :param url: GELF HTTP input pattern. Default is '/gelp' as specified in the documentation (2.2)
        """

        Handler.__init__(self)
        BaseHandler.__init__(self, **kwargs)

        self.host = host
        self.port = port
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.compress = False
        self.timeout = timeout

    def prepareLogRecord(self, record):
        data = gelf.make(record, self.domain, self.debug, self.version, self.additional_fields, self.include_extra_fields)
        return gelf.pack(data, self.compress)

    def emit(self, record):

        try:
            data = self.prepareLogRecord(record)
            http_conn = httplib.HTTPConnection(host=self.host, port=self.port, timeout=self.timeout)
            http_conn.request("POST", self.url, data, self.headers)
            response = http_conn.getresponse()

            if response.status not in [202, "202"]:
                raise Exception("GelfHttpHandler: response status {} is not the expected 202" % response.status)

        except Exception:
            self.handleError(record)
