pygelf
======

.. image:: https://github.com/keeprocking/pygelf/actions/workflows/tests.yml/badge.svg?branch=master
   :target: https://github.com/keeprocking/pygelf/actions
.. image:: https://coveralls.io/repos/github/keeprocking/pygelf/badge.svg?branch=master
   :target: https://coveralls.io/github/keeprocking/pygelf?branch=master
.. image:: https://badge.fury.io/py/pygelf.svg
   :target: https://pypi.python.org/pypi/pygelf
.. image:: https://img.shields.io/pypi/dm/pygelf
   :target: https://pypi.python.org/pypi/pygelf

Python logging handlers with GELF (Graylog Extended Log Format) support.

Currently TCP, UDP, TLS (encrypted TCP) and HTTP logging handlers are supported.

Get pygelf
==========
.. code:: python

    pip install pygelf

Usage
=====

.. code:: python

    from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler, GelfHttpHandler, GelfHttpsHandler
    import logging


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(GelfTcpHandler(host='127.0.0.1', port=9401))
    logger.addHandler(GelfUdpHandler(host='127.0.0.1', port=9402))
    logger.addHandler(GelfTlsHandler(host='127.0.0.1', port=9403))
    logger.addHandler(GelfHttpHandler(host='127.0.0.1', port=9404))
    logger.addHandler(GelfHttpsHandler(host='127.0.0.1', port=9405))

    logger.info('hello gelf')

Message structure
=================

According to the GELF spec, each message has the following mandatory fields:

- **version**: '1.1', can be overridden when creating a logger
- **short_message**: the log message itself
- **timestamp**: current timestamp
- **level**: syslog-compliant_ log level number (e.g. WARNING will be sent as 4)
- **host**: hostname of the machine that sent the message
- **full_message**: this field contains stack trace and is being written **ONLY** when logging an exception, e.g.

.. code:: python

    try:
        1/0
    except ZeroDivisionError as e:
        logger.exception(e)

.. _syslog-compliant: https://en.wikipedia.org/wiki/Syslog#Severity_level

In debug mode (when handler was created with debug=True option) each message contains some extra fields (which are pretty self-explanatory): 

- **_file**
- **_line**
- **_module**
- **_func**
- **_logger_name**

Configuration
=============

Each handler has the following parameters:

- **host**: IP address of the GELF input
- **port**: port of the GELF input
- **debug** (False by default): if true, each log message will include debugging info: module name, file name, line number, method name
- **version** ('1.1' by default): GELF protocol version, can be overridden
- **include_extra_fields** (False by default): if true, each log message will include all the extra fields set to LogRecord
- **json_default** (:code:`str` with exception for several :code:`datetime` objects): function that is called for objects that cannot be serialized to JSON natively by python. Default implementation is custom function that returns result of :code:`isoformat()` method for :code:`datetime.datetime`, :code:`datetime.time`, :code:`datetime.date` objects and result of :code:`str(obj)` call for other objects (which is string representation of an object with fallback to :code:`repr`)

Also, there are some handler-specific parameters.

UDP:

- **chunk\_size** (1300 by default) - maximum length of the message. If log length exceeds this value, it splits into multiple chunks (see https://www.graylog.org/resources/gelf/ section "chunked GELF") with the length equals to this value. This parameter must be less than the MTU_. If the logs don't seem to be delivered, try to reduce this value.
- **compress** (True by default) - if true, compress log messages before sending them to the server

.. _MTU: https://en.wikipedia.org/wiki/Maximum_transmission_unit

TLS:

- **validate** (False by default) - if true, validate server certificate. If server provides a certificate that doesn't exist in **ca_certs**, you won't be able to send logs over TLS
- **ca_certs** (None by default) - path to CA bundle file. This parameter is required if **validate** is true.
- **certfile** (None by default) - path to certificate file that will be used to identify ourselves to the remote endpoint. This is necessary when the remote server has client authentication required. If **certfile** contains the private key, it should be placed before the certificate.
- **keyfile** (None by default) - path to the private key. If the private key is stored in **certfile** this parameter can be None.

HTTP:

- **compress** (True by default) - if true, compress log messages before sending them to the server
- **path** ('/gelf' by default) - path of the HTTP input (http://docs.graylog.org/en/latest/pages/sending_data.html#gelf-via-http)
- **timeout** (5 by default) - amount of seconds that HTTP client should wait before it discards the request if the server doesn't respond

HTTPS:

- **compress** (True by default) - if true, compress log messages before sending them to the server
- **path** ('/gelf' by default) - path of the HTTP input (http://docs.graylog.org/en/latest/pages/sending_data.html#gelf-via-http)
- **timeout** (5 by default) - amount of seconds that HTTP client should wait before it discards the request if the server doesn't respond
- **validate** whether or not to validate the input's certificate
- **param ca_certs** path to the CA certificate file that signed the certificate the input is using
- **param certfile** not yet used
- **param keyfile** not yet used
- **param keyfile_password** not yet used

Static fields
=============

If you need to include some static fields into your logs, simply pass them to the handler constructor. Each additional field should start with underscore. You can't add field '\_id'.

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
            record.job_id = threading.local().process_id
            return True

    logger.addFilter(ContextFilter())
    handler = GelfUdpHandler(host='127.0.0.1', port=9402, include_extra_fields=True)
    logger.addHandler(handler)

Defining fields from environment
================================

If you need to include some fields from the environment into your logs, add them to record by using `additional_env_fields`.

The following example will add an `env` field to the logs, taking its value from the environment variable `FLASK_ENV`.

.. code:: python

    handler = GelfTcpHandler(host='127.0.0.1', port=9402, include_extra_fields=True, additional_env_fields={'env': 'FLASK_ENV'})
    logger.addHandler(handler)

The following can also be used in defining logging from configuration files (yaml/ini):

.. code:: ini

    [formatters]
    keys=standard

    [formatter_standard]
    class=logging.Formatter
    format=%(message)s

    [handlers]
    keys=graylog

    [handler_graylog]
    class=pygelf.GelfTcpHandler
    formatter=standard
    args=('127.0.0.1', '12201')
    kwargs={'include_extra_fields': True, 'debug': True, 'additional_env_fields': {'env': 'FLASK_ENV'}}

    [loggers]
    keys=root

    [logger_root]
    level=WARN
    handlers=graylog

Running tests
=============

To run tests, you'll need tox_. After installing, simply run it:

.. code::

    tox

.. _tox: https://pypi.python.org/pypi/tox
