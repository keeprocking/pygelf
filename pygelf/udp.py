from logging.handlers import DatagramHandler
from pygelf.gelfmessage import GelfMessage


class GelfUdpHandler(DatagramHandler):

    def __init__(self, host, port, debug=False, chunk_size=1000, **kwargs):
        super(GelfUdpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug
        self.chunk_size = chunk_size

        self.additional_fields.pop('_id', None)

    def send(self, s):
        pass

    def makePickle(self, record):
        message = GelfMessage(record, self.debug, self.additional_fields)
        return message.pack()
