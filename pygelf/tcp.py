from logging.handlers import SocketHandler
from pygelf.gelfmessage import GelfMessage
import json


_ignore_fields = ('id', '_id')


class GelfTcpHandler(SocketHandler):

    def __init__(self, host, port, debug=False, **kwargs):
        """
        :param host: gelf tcp input host
        :param port: gelf tcp input port
        :param debug: include debug fields, e.g. line number
        :param kwargs: additional fields that will be included in the log message, e.g. app name
        """

        super(GelfTcpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug

        for field in _ignore_fields:
            self.additional_fields.pop(field, None)

    def makePickle(self, record):
        message = vars(GelfMessage(record, self.debug))
        message.update(self.additional_fields)
        packed = json.dumps(message) + '\0'
        return packed.encode('utf-8')
