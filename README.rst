Get pygelf
==========
::

    pip install pygelf

Usage
=====

Currently TCP, UDP and TLS (encrypted TCP) handlers are supported.

::

    from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
    import logging


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(GelfTcpHandler(host='127.0.0.1', port=9401, compress=False))
    logger.addHandler(GelfUdpHandler(host='127.0.0.1', port=9402, debug=True, chunk_size=1350))
    logger.addHandler(GelfTlsHandler(host='127.0.0.1', port=9403, validate=True, ca_certs='/etc/ssl/certs/ca-ceritficates.crt'))

    logging.info('hello gelf')

Configuration
=============


Each handler has the following parameters:

- **host**: ip address of the GELF input
- **port**: port of the GELF input
- **debug** (false by default): if true, each log message will include debugging info: module name, file name, line number, method name
- **compress** (true by default): if true, compress log messages before send them to the server

In addition UDP and TLS handlers have some specific parameters.

UDP:

- **chunk\_size** (1300 by default) - maximum length of the message. If log length exceeds this value, it splits into multiple chunks (see https://www.graylog.org/resources/gelf/ section "chunked GELF") with the length equals to this value. This parameter must be less than the MTU_. If the logs don't seem to be delivered, try to reduce this value.

.. _MTU: https://en.wikipedia.org/wiki/Maximum_transmission_unit

TLS:

- **validate** (false by default) - if true, validate server certificate. If server provides a certificate that doesn't exist in **ca_certs**, you won't be able to send logs over TLS
- **ca_certs** (none by default) - path to CA bundle file. This parameter is required if **validate** is true.

Additional fields
=================

If you need to include some static fields into your logs, simply pass them to the constructor of the handler. Each additional field shoud start with underscore. You can't add field '\_id'.

Example:

::

    handler = GelfUdpHandler(host='127.0.0.1', port=9402, _app_name='pygelf', _something=11)
    logger.addHandler(handler)

Or using kwargs:

::

    fields = {
        '_app_name': 'gelf_test',
        '_app_version': '1.5',
        '_something': 11
    }
    
    handler = GelfUdpHandler(host='127.0.0.1', port=9402, **fields)
    logger.addHandler(handler)

