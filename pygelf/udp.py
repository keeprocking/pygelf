from logging.handlers import DatagramHandler
from pygelf.gelf import make_gelf, pack_gelf


MAX_MESSAGE_LENGTH = 1


class GelfUdpHandler(DatagramHandler):

    def __init__(self, host, port, debug=False, compress=True, chunk_size=1000, **kwargs):
        super(GelfUdpHandler, self).__init__(host, port)
        self.additional_fields = kwargs
        self.debug = debug
        self.compress = compress
        self.chunk_size = chunk_size
        self.additional_fields.pop('_id', None)

    def send(self, s):
        pass

    def makePickle(self, record):
        gelf = make_gelf(record, self.debug, self.additional_fields)
        packed = pack_gelf(gelf, self.compress)
        return packed

    def split_message(self):
        pass
