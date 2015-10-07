from setuptools import setup


setup(
    name='pygelf',
    version='0.2.2',
    packages=['pygelf'],
    description='Python logging handlers for sending logs to Graylog over TCP and UDP',
    keywords='logging udp tcp ssl tls graylog2 graylog gelf',
    author='Ivan Mukhin',
    author_email='muhin.ivan@gmail.com',
    url='https://github.com/keeprocking/pygelf',
    long_description=open('README.rst').read(),
    license='MIT'
)
