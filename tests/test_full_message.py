from unittest import TestCase
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import logging


class TestFullMessage(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger('test')

    def setUp(self):
        self.handler = GelfTcpHandler(host='127.0.0.1', port=12201)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_full_message(self):
        message = get_unique_message();

        try:
            raise Exception(message)
        except Exception as e:
            parsed_message = log_exception(self.logger, message, e)
            self.assertEqual(message, parsed_message['message'])
            self.assertIn(message, parsed_message['full_message'])
            self.assertIn('Traceback (most recent call last)', parsed_message['full_message'])
            self.assertIn('Exception: ', parsed_message['full_message'])
