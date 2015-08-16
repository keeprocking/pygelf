Get pygelf
==========
::

    pip install pygelf

Usage
=====
::

    from pygelf import GelfTcpHandler, GelfUdpHandler
    import logging


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(GelfTcpHandler('127.0.0.1', 9401))
    logger.addHandler(GelfUdpHandler('127.0.0.1', 9402))

    logging.info('hello gelf')

Configuration
=============

Each handler has the following parameters:

- **host**: ip address of the GELF input
- **port**: port of the GELF input
- **debug** (false by default): if true, each log message will include debugging info: module name, file name, line number, method name
- **compress** (true by default): if true, compress log messages before send them to the server

In addition, UDP handler has one extra field:

- **chunk\_size** (1300 by default) - maximum length of the message. If log length exceeds this value, it splits into multiple chunks (see https://www.graylog.org/resources/gelf-2/ section "chunked GELF") with the length equals to this value. This parameter must be less than the `MTU <https: en.wikipedia.org="" wiki="" maximum_transmission_unit="">`__. If the logs don't seem to be delivered, try to reduce this value.

Additional fields
=================

If you need to include some static fields into your logs, simply pass them to the constructor of the handler. Each additional field shoud start with underscore. You can't add field '\_id' as well.

Example:

::

    handler = GelfUdpHandler('127.0.0.1', 9402, _app_name='pygelf', _something=11)
    logger.addHandler(handler)

Or using kwargs:

::

    fields = {
        '_app_name': 'gelf_test',
        '_app_version': '1.5',
        '_something': 11
    }
    
    handler = GelfUdpHandler('127.0.0.1', 9402, **fields)
    logger.addHandler(handler)

