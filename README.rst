pygelf
======

.. image:: https://travis-ci.org/keeprocking/pygelf.svg?branch=master
    :target: https://travis-ci.org/keeprocking/pygelf

Python logging handlers with GELF (Graylog Extended Log Format) support.

Currently TCP, UDP and TLS (encrypted TCP) logging handlers are supported.

Get pygelf
==========
.. code:: python

    pip install pygelf

Usage
=====

.. code:: python

    from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler
    import logging


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(GelfTcpHandler(host='127.0.0.1', port=9401, debug=True))
    logger.addHandler(GelfUdpHandler(host='127.0.0.1', port=9402, compress=True, chunk_size=1350))
    logger.addHandler(GelfTlsHandler(host='127.0.0.1', port=9403, validate=True, ca_certs='/etc/ssl/certs/ca-ceritficates.crt'))

    logging.info('hello gelf')

Configuration
=============


Each handler has the following parameters:

- **host**: ip address of the GELF input
- **port**: port of the GELF input
- **debug** (false by default): if true, each log message will include debugging info: module name, file name, line number, method name
- **version** ('1.1' by default): GELF protocol version, can be overridden by a client
- **include_extra_fields** (False by default): if true, each log message will include all the extra fields set to LogRecord

In addition UDP and TLS handlers have some specific parameters.

UDP:

- **chunk\_size** (1300 by default) - maximum length of the message. If log length exceeds this value, it splits into multiple chunks (see https://www.graylog.org/resources/gelf/ section "chunked GELF") with the length equals to this value. This parameter must be less than the MTU_. If the logs don't seem to be delivered, try to reduce this value.
- **compress** (true by default): if true, compress log messages before send them to the server

.. _MTU: https://en.wikipedia.org/wiki/Maximum_transmission_unit

TLS:

- **validate** (false by default) - if true, validate server certificate. If server provides a certificate that doesn't exist in **ca_certs**, you won't be able to send logs over TLS
- **ca_certs** (none by default) - path to CA bundle file. This parameter is required if **validate** is true.

Additional fields
=================

If you need to include some static fields into your logs, simply pass them to the handler constructor. Each additional field shoud start with underscore. You can't add field '\_id'.

Example:

.. code:: python

    handler = GelfUdpHandler(host='127.0.0.1', port=9402, _app_name='pygelf', _something=11)
    logger.addHandler(handler)

Extra fields
============

If you need to include some dynamic fields into your logs, add them to record by using LoggingAdapter or logging.Filter and create handler with include_extra_fields set to True.
All the non-trivial fields of the record will be sent to graylog2 with '\_' added before the name

 Example:

 .. code:: python

    class ContextFilter(logging.Filter):

        def filter(self, record):
            record.job_id = threading.local().process_id # logging job_id of currently processed job
            return True

    logger.addFilter(ContextFilter())
    handler = GelfUdpHandler(host='127.0.0.1', port=9402, include_extra_fields=True)
    logger.addHandler(handler)

Running tests
=============

To run tests, you'll need tox_. After installing, simply run it:

.. code::

    tox

You can also specify interpreter version. For example:

.. code::

    tox -e py26
    tox -e py35

.. _tox: https://pypi.python.org/pypi/tox

