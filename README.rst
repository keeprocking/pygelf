pygelf
======
|travis| |pypi|

.. |travis| image:: https://travis-ci.org/keeprocking/pygelf.svg?branch=master
   :target: https://travis-ci.org/keeprocking/pygelf
.. |pypi| image:: https://badge.fury.io/py/pygelf.svg
    :target: https://badge.fury.io/py/pygelf

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

Message structure
=================

According to the GELF spec, each message has the following mandatory fields:

- **version**: '1.1', can be overridden when creating a logger
- **short_message**: the log message itself
- **timestamp**: current timestamp
- **level**: log level (debug, warning, etc.)
- **source**: FQDN_ of the machine that sent the message
- **full_message**: this field contains stack trace and is being written **ONLY** when logging an exception, e.g.

.. code:: python

    try:
        1/0
    except ZeroDivisionError as e:
        logging.exception(e)

.. _FQDN: https://en.wikipedia.org/wiki/Fully_qualified_domain_name

In debug mode (when handler was created with debug=True option) each message contains some extra fields (which are pretty self-explanatory): 

- **_file**
- **_line**
- **_module**
- **_func**

Configuration
=============

Each handler has the following parameters:

- **host**: IP address of the GELF input
- **port**: port of the GELF input
- **debug** (False by default): if true, each log message will include debugging info: module name, file name, line number, method name
- **version** ('1.1' by default): GELF protocol version, can be overridden
- **include_extra_fields** (False by default): if true, each log message will include all the extra fields set to LogRecord

In addition UDP and TLS handlers have some specific parameters.

UDP:

- **chunk\_size** (1300 by default) - maximum length of the message. If log length exceeds this value, it splits into multiple chunks (see https://www.graylog.org/resources/gelf/ section "chunked GELF") with the length equals to this value. This parameter must be less than the MTU_. If the logs don't seem to be delivered, try to reduce this value.
- **compress** (True by default): if true, compress log messages before send them to the server

.. _MTU: https://en.wikipedia.org/wiki/Maximum_transmission_unit

TLS:

- **validate** (False by default) - if true, validate server certificate. If server provides a certificate that doesn't exist in **ca_certs**, you won't be able to send logs over TLS
- **ca_certs** (None by default) - path to CA bundle file. This parameter is required if **validate** is true.
- **certfile** (None by default) - path to certificate file that will be used to identify ourselves to the remote endpoint. This is necessary when the remote server has client authentication required. If **certfile** contains the private key, it should be placed before the certificate.
- **keyfile** (None by default) - path to the private key. If the private key is stored in **certfile** this parameter can be None.

Static fields
=============

If you need to include some static fields into your logs, simply pass them to the handler constructor. Each additional field shoud start with underscore. You can't add field '\_id'.

Example:

.. code:: python

    handler = GelfUdpHandler(host='127.0.0.1', port=9402, _app_name='pygelf', _something=11)
    logger.addHandler(handler)

Dynamic fields
==============

If you need to include some dynamic fields into your logs, add them to record by using LoggingAdapter or logging.Filter and create handler with include_extra_fields set to True.
All the non-trivial fields of the record will be sent to graylog2 with '\_' added before the name

 Example:

 .. code:: python

    class ContextFilter(logging.Filter):

        def filter(self, record):
            record.job_id = threading.local().process_id  # logging job_id of currently processed job
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

