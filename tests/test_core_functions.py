from pygelf import gelf
import json
import zlib
import struct
import pytest


@pytest.mark.parametrize('compress', [True, False])
def test_pack(compress):
    message = {'version': '1.1', 'short_message': 'test pack'}
    packed_message = gelf.pack(message, compress)
    unpacked_message = zlib.decompress(packed_message) if compress else packed_message
    unpacked_message = json.loads(unpacked_message.decode('utf-8'))
    assert message == unpacked_message


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
