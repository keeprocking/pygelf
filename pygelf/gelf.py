import logging
import json
import zlib
import os
import struct
import socket


_levels = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2
}


def make(record, debug, additional_fields):
    gelf = {
        'version': '1.1',
        'short_message': record.msg,
        'full_message': record.exc_text,
        'timestamp': record.created,
        'level': _levels[record.levelno],
        'source': socket.getfqdn()
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


def pack(gelf, compress):
    packed = json.dumps(gelf).encode('utf8')
    return zlib.compress(packed) if compress else packed


def split(gelf, chunk_size):
    header = b'\x1e\x0f'
    message_id = os.urandom(8)
    chunks = [gelf[pos:pos+chunk_size] for pos in range(0, len(gelf), chunk_size)]
    number_of_chunks = struct.pack('b', len(chunks))

    for chunk_index, chunk in enumerate(chunks):
        yield b''.join((
            header,
            message_id,
            struct.pack('b', chunk_index),
            number_of_chunks,
            chunk
        ))
