from logging.handlers import SocketHandler
from pygelf.gelfmessage import GelfMessage
import json


class GelfTcpHandler(SocketHandler):

    def __init__(self, host, port, debug=False, **kwargs):
        super(GelfTcpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug

    def makePickle(self, record):
        message = vars(GelfMessage(record, self.debug))
        message.update(self.additional_fields)
        packed = json.dumps(message) + '\0'
        return packed.encode('utf-8')
