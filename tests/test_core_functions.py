import datetime
import json
import struct
import zlib

import pytest

from pygelf import gelf


class _ObjWithStr:
    def __str__(self):
        return 'str'


class _ObjWithRepr:
    def __repr__(self):
        return 'repr'


_now = datetime.datetime.now()


@pytest.mark.parametrize(
    ('obj', 'expected'),
    [
        (_ObjWithStr(), 'str'),
        (_ObjWithRepr(), 'repr'),
        (_now, _now.isoformat()),
        (_now.time(), _now.time().isoformat()),
        (_now.date(), _now.date().isoformat()),
    ]
)
def test_object_to_json(obj, expected):
    result = gelf.object_to_json(obj)
    assert result == expected


@pytest.mark.parametrize('compress', [True, False])
def test_pack(compress):
    message = {'version': '1.1', 'short_message': 'test pack', 'foo': _ObjWithStr()}
    expected = json.loads(json.dumps(message, default=str))
    packed_message = gelf.pack(message, compress, default=str)
    unpacked_message = zlib.decompress(packed_message) if compress else packed_message
    unpacked_message = json.loads(unpacked_message.decode('utf-8'))
    assert expected == unpacked_message


def test_split():
    message = b'12345'
    header = b'\x1e\x0f'
    chunks = list(gelf.split(message, 2))
    expected = [
        (struct.pack('b', 0), struct.pack('b', 3), b'12'),
        (struct.pack('b', 1), struct.pack('b', 3), b'34'),
        (struct.pack('b', 2), struct.pack('b', 3), b'5')
    ]

    assert len(chunks) == len(expected)

    for index, chunk in enumerate(chunks):
        expected_index, expected_chunks_count, expected_chunk = expected[index]
        assert chunk[:2] == header
        assert chunk[10:11] == expected_index
        assert chunk[11:12] == expected_chunks_count
        assert chunk[12:] == expected_chunk
