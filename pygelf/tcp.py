from logging.handlers import SocketHandler
from pygelf import gelf


class GelfTcpHandler(SocketHandler):

    def __init__(self, host, port, debug=False, **kwargs):
        """
        Logging handler that transforms each record into GELF (graylog extended log format) and sends it over tcp.

        :param host: gelf tcp input host
        :param port: gelf tcp input port
        :param debug: include debug fields, e.g. line number, or not
        :param kwargs: additional fields that will be included in the log message, e.g. application name.
                       Each additional field should start with underscore, e.g. _app_name
        """

        super(GelfTcpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug
        self.additional_fields.pop('_id', None)

    def makePickle(self, record):
        message = gelf.make(record, self.debug, self.additional_fields)
        packed = gelf.pack(message)

        """ if you send the message over tcp, it should always be null terminated or the input will reject it """
        return packed + b'\x00'
