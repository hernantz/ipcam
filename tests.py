import unittest
from ipcam import IPCam


TEST_IP = '192.168.1.99'
TEST_PORT = 99
TEST_USER = 'admin'
TEST_PASSWORD = ''


class IPCamTestCase(unittest.TestCase):
    def setUp(self):
        self.ipcam = IPCam(TEST_IP, TEST_PORT,
                           user=TEST_USER, password=TEST_PASSWORD)

    def test_parse_status_response(self):
        pass
