import datetime
import logging
import json
import zlib
import os
import struct
import traceback


LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2
}


# skip_list is used to filter additional fields in a log message.
# It contains all attributes listed in
# http://docs.python.org/library/logging.html#logrecord-attributes
# plus exc_text, which is only found in the logging module source,
# and id, which is prohibited by the GELF format.
SKIP_LIST = (
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName'
)


def make(record, domain, debug, version, additional_fields, additional_env_fields, include_extra_fields=False):
    gelf = {
        'version': version,
        'short_message': record.getMessage(),
        'timestamp': record.created,
        'level': LEVELS[record.levelno],
        'host': domain
    }

    if record.exc_info:
        gelf['full_message'] = '\n'.join(traceback.format_exception(*record.exc_info))
    elif record.exc_text is not None:
        # QueueHandler, if used, formats the record, so that exc_info will always be empty:
        # https://docs.python.org/3/library/logging.handlers.html#logging.handlers.QueueHandler
        gelf['full_message'] = record.exc_text

    if debug:
        gelf['_file'] = record.filename
        gelf['_line'] = record.lineno
        gelf['_module'] = record.module
        gelf['_func'] = record.funcName
        gelf['_logger_name'] = record.name

    if additional_fields is not None:
        gelf.update(additional_fields)

    if additional_env_fields is not None:
        appended = {}
        for name, env in additional_env_fields.items():
            if env in os.environ:
                appended["_" + name] = os.environ.get(env)

        gelf.update(appended)

    if include_extra_fields:
        add_extra_fields(gelf, record)

    return gelf


def add_extra_fields(gelf, record):
    for key, value in record.__dict__.items():
        if key not in SKIP_LIST and not key.startswith('_'):
            gelf[f'_{key}'] = value


def object_to_json(obj):
    """Convert object that cannot be natively serialized by python to JSON representation."""
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    return str(obj)


def pack(gelf, compress, default):
    packed = json.dumps(gelf, separators=(',', ':'), default=default).encode('utf-8')
    return zlib.compress(packed) if compress else packed


def split(gelf, chunk_size):
    header = b'\x1e\x0f'
    message_id = os.urandom(8)
    chunks = [gelf[pos:pos + chunk_size] for pos in range(0, len(gelf), chunk_size)]
    number_of_chunks = len(chunks)

    for chunk_index, chunk in enumerate(chunks):
        yield b''.join((
            header,
            message_id,
            struct.pack('b', chunk_index),
            struct.pack('b', number_of_chunks),
            chunk
        ))
