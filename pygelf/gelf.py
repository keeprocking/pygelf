import logging
import json
import zlib
import os
import struct
import traceback


_levels = {
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
_skip_list = (
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName'
)


def make(record, domain, debug, version, additional_fields, include_extra_fields=False):
    stack_trace = None
    if record.exc_info is not None:
        stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))

    gelf = {
        'version': version,
        'short_message': record.getMessage(),
        'full_message': stack_trace,
        'timestamp': record.created,
        'level': _levels[record.levelno],
        'source': domain,  # TODO: should be deprecated sooner or later
        'host': domain
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

    if include_extra_fields:
        add_extra_fields(gelf, record)

    return gelf


def add_extra_fields(gelf, record):
    for key, value in record.__dict__.items():
        if key not in _skip_list and not key.startswith('_'):
            gelf['_%s' % key] = value


def pack(gelf, compress=False):
    packed = json.dumps(gelf).encode('utf-8')
    return zlib.compress(packed) if compress else packed


def split(gelf, chunk_size):
    header = b'\x1e\x0f'
    message_id = os.urandom(8)
    chunks = [gelf[pos:pos+chunk_size] for pos in range(0, len(gelf), chunk_size)]
    number_of_chunks = len(chunks)

    for chunk_index, chunk in enumerate(chunks):
        yield b''.join((
            header,
            message_id,
            struct.pack('b', chunk_index),
            struct.pack('b', number_of_chunks),
            chunk
        ))
