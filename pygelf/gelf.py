import logging
import json


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

    message = {
        'version': '1.1',
        'short_message': record.message,
        'full_message': record.exc_text,
        'timestamp': record.created,
        'level': _levels[record.levelno],
    }
    
    if debug:
        message.update({
            '_file': record.filename,
            '_line': record.lineno,
            '_module': record.module,
            '_func': record.funcName
        })

    if additional_fields is not None:
        message.update(additional_fields)

    return json.dumps(message)
