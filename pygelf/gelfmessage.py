import logging
import json


_levels = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2
}


class GelfMessage:

    def __init__(self, record, debug, additional_fields):
        self.version = '1.1'
        self.short_message = record.message
        self.full_message = record.exc_text
        self.timestamp = record.created
        self.level = _levels[record.levelno]

        if debug:
            self._file = record.filename
            self._line = record.lineno
            self._module = record.module
            self._func = record.funcName

        if additional_fields:
            vars(self).update(additional_fields)

    def pack(self):
        message = vars(self)
        packed = json.dumps(message)
        return packed.encode('utf-8')
