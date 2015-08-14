import logging
import json
import zlib


_levels = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2
}


def make_gelf(record, debug, additional_fields):
    """

    :param record:
    :param debug:
    :param additional_fields:
    :return:
    """

    gelf = {
        'version': '1.1',
        'short_message': record.message,
        'full_message': record.exc_text,
        'timestamp': record.created,
        'level': _levels[record.levelno],
    }
    
    if debug:
        gelf.update({
            '_file': record.filename,
            '_line': record.lineno,
            '_module': record.module,
            '_func': record.funcName
        })

    if additional_fields is not None:
        gelf.update(additional_fields)

    return gelf


def pack_gelf(gelf, compress):
    packed = json.dumps(gelf).encode('utf8')
    return zlib.compress(packed) if compress else packed

