from logging.handlers import DatagramHandler
from pygelf.gelf import make_gelf


MAX_MESSAGE_LENGTH = 1


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
        gelf = make_gelf(record, self.debug, self.additional_fields)
        return gelf.encode('utf8')

    def split_message(self):
        pass
