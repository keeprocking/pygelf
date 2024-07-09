import ssl
import socket

try:
    import httplib
except ImportError:
    import http.client as httplib

from logging.handlers import SocketHandler, DatagramHandler
from logging import Handler as LoggingHandler
from pygelf import gelf


class BaseHandler:
    def __init__(self, debug=False, version='1.1', include_extra_fields=False, compress=False,
                 static_fields=None, json_default=gelf.object_to_json, additional_env_fields=None, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over TCP.

        :param debug: include debug fields, e.g. line number, or not
        :param include_extra_fields: include non-default fields from record to message, or not
        :param json_default: function that is called for objects that cannot be serialized to JSON natively by python
        :param kwargs: additional fields that will be included in the log message, e.g. application name.
                       Each additional field should start with underscore, e.g. _app_name
        """

        self.additional_env_fields = additional_env_fields
        if self.additional_env_fields is None:
            self.additional_env_fields = {}

        self.debug = debug
        self.version = version
        self.additional_fields = static_fields if static_fields else kwargs
        self.include_extra_fields = include_extra_fields
        self.additional_fields.pop('_id', None)
        self.domain = socket.gethostname()
        self.compress = compress
        self.json_default = json_default

    def convert_record_to_gelf(self, record):
        return gelf.pack(
            gelf.make(record, self.domain, self.debug, self.version, self.additional_fields,
                      self.additional_env_fields, self.include_extra_fields),
            self.compress, self.json_default
        )


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
        """ if you send the message over tcp, it should always be null terminated or the input will reject it """
        return self.convert_record_to_gelf(record) + b'\x00'


class GelfUdpHandler(BaseHandler, DatagramHandler):

    def __init__(self, host, port, compress=True, chunk_size=1300, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over UDP.
        If message length exceeds chunk_size, the message splits into multiple chunks.
        The number of chunks must be less than 128.

        :param host: GELF UDP input host
        :param port: GELF UDP input port
        :param compress: compress message before sending it to the server or not
        :param chunk_size: length of a chunk, should be less than the MTU (maximum transmission unit)
        """

        DatagramHandler.__init__(self, host, port)
        BaseHandler.__init__(self, compress=compress, **kwargs)

        self.chunk_size = chunk_size

    def send(self, s):
        if len(s) <= self.chunk_size:
            DatagramHandler.send(self, s)
            return

        chunks = gelf.split(s, self.chunk_size)
        for chunk in chunks:
            DatagramHandler.send(self, chunk)

    def makePickle(self, record):
        return self.convert_record_to_gelf(record)


class GelfTlsHandler(GelfTcpHandler):

    def __init__(self, validate=False, ca_certs=None, certfile=None, keyfile=None, **kwargs):
        """
        TCP GELF logging handler with TLS support

        :param validate: if true, validate server certificate. In that case ca_certs are required
        :param ca_certs: path to CA bundle file. For instance, on CentOS it would be '/etc/pki/tls/certs/ca-bundle.crt'
        :param certfile: path to the certificate file that is used to identify ourselves to the server
        :param keyfile: path to the private key. If the private key is stored with the certificate,
                        this parameter can be ignored
        """

        if validate and ca_certs is None:
            raise ValueError('CA bundle file path must be specified')

        if keyfile is not None and certfile is None:
            raise ValueError('certfile must be specified')

        GelfTcpHandler.__init__(self, **kwargs)

        self.ca_certs = ca_certs
        self.reqs = ssl.CERT_REQUIRED if validate else ssl.CERT_NONE
        self.certfile = certfile
        self.keyfile = keyfile if keyfile else certfile

    def makeSocket(self, timeout=1):
        plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if hasattr(plain_socket, 'settimeout'):
            plain_socket.settimeout(timeout)

        wrapped_socket = ssl.wrap_socket(plain_socket, ca_certs=self.ca_certs, cert_reqs=self.reqs,
                                         keyfile=self.keyfile, certfile=self.certfile)
        wrapped_socket.connect((self.host, self.port))

        return wrapped_socket


class GelfHttpHandler(BaseHandler, LoggingHandler):

    def __init__(self, host, port, compress=True, path='/gelf', timeout=5, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over HTTP.

        :param host: GELF HTTP input host
        :param port: GELF HTTP input port
        :param compress: compress message before sending it to the server or not
        :param path: path of the HTTP input (http://docs.graylog.org/en/latest/pages/sending_data.html#gelf-via-http)
        :param timeout: amount of seconds that HTTP client should wait before it discards the request
                        if the server doesn't respond
        """

        LoggingHandler.__init__(self)
        BaseHandler.__init__(self, compress=compress, **kwargs)

        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self.headers = {}

        if compress:
            self.headers['Content-Encoding'] = 'gzip,deflate'

    def emit(self, record):
        data = self.convert_record_to_gelf(record)
        connection = httplib.HTTPConnection(host=self.host, port=self.port, timeout=self.timeout)
        connection.request('POST', self.path, data, self.headers)


class GelfHttpsHandler(BaseHandler, LoggingHandler):

    def __init__(self, host, port, compress=True, path='/gelf', timeout=5, validate=False,
                 ca_certs=None, certfile=None, keyfile=None, keyfile_password=None, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over HTTP.

        :param host: GELF HTTP input host
        :param port: GELF HTTP input port
        :param compress: compress message before sending it to the server or not
        :param path: path of the HTTP input (http://docs.graylog.org/en/latest/pages/sending_data.html#gelf-via-http)
        :param timeout: amount of seconds that HTTP client should wait before it discards the request
                        if the server doesn't respond
        :param validate: whether or not to validate the input's certificate
        :param ca_certs: path to the CA certificate file that signed the certificate the input is using
        :param certfile: not yet used
        :param keyfile: not yet used
        :param keyfile_password: not yet used
        """

        LoggingHandler.__init__(self)
        BaseHandler.__init__(self, compress=compress, **kwargs)

        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self.headers = {}
        self.ca_certs = ca_certs
        self.keyfile = keyfile
        self.certfile = certfile
        self.keyfile_password = keyfile_password

        # Set up context: https://docs.python.org/3/library/http.client.html#http.client.HTTPSConnection
        # create_default_context returns an SSLContext object
        self.ctx = ssl.create_default_context()

        if validate and ca_certs is None:
            raise ValueError('CA bundle file path must be specified')

        if not validate:
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE
        else:
            # Load our CA file
            self.ctx.load_verify_locations(cafile=self.ca_certs)

        if compress:
            self.headers['Content-Encoding'] = 'gzip,deflate'

    def emit(self, record):
        data = self.convert_record_to_gelf(record)
        connection = httplib.HTTPSConnection(host=self.host, port=self.port, context=self.ctx, timeout=self.timeout)
        connection.request('POST', self.path, data, self.headers)
