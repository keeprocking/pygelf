from logging.handlers import DatagramHandler
from pygelf import gelf


class GelfUdpHandler(DatagramHandler):

    def __init__(self, host, port, debug=False, compress=True, chunk_size=1300, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over udp.
        If message length exceeds chunk_size, the message splits into multiple chunks.
        The number of chunks must be less than 128.

        :param host: gelf tcp input host
        :param port: gelf tcp input port
        :param debug: include debug fields, e.g. line number, or not
        :param compress: compress message before send it to the server or not
        :param chunk_size: length of a chunk, should be less than the MTU (maximum transmission unit)
        :param kwargs: additional fields that will be included in the log message, e.g. application name.
                       Each additional field should start with underscore, e.g. _app_name
        """

        super(GelfUdpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug
        self.compress = compress
        self.chunk_size = chunk_size
        self.additional_fields.pop('_id', None)

    def send(self, s):
        if len(s) <= self.chunk_size:
            super(GelfUdpHandler, self).send(s)
        else:
            chunks = gelf.split(s, self.chunk_size)
            for chunk in chunks:
                super(GelfUdpHandler, self).send(chunk)

    def makePickle(self, record):
        message = gelf.make(record, self.debug, self.additional_fields)
        packed = gelf.pack(message, self.compress)
        return packed
