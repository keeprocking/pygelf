from setuptools import setup


setup(
    name='pygelf',
    version='0.4.2',
    packages=['pygelf'],
    description='Logging handlers with GELF support',
    keywords='logging udp tcp ssl tls graylog2 graylog gelf',
    author='Ivan Mukhin',
    author_email='muhin.ivan@gmail.com',
    url='https://github.com/keeprocking/pygelf',
    long_description=open('README.rst').read(),
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
