from setuptools import setup


setup(
    name='pygelf',
    version='0.2.5',
    packages=['pygelf'],
    description='Logging handlers for sending messages into Graylog',
    keywords='logging udp tcp ssl tls graylog2 graylog gelf',
    author='Ivan Mukhin',
    author_email='muhin.ivan@gmail.com',
    url='https://github.com/keeprocking/pygelf',
    long_description=open('README.rst').read(),
    license='MIT'
)
