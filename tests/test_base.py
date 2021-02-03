import unittest
from app.calcdb import base
from app import settings

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.q = base.DB(settings.PG_DB)

    def tearDown(self):
        self.q.close()

    def test_get_down_brch(self):
        cc = "360104XH"   
        print(self.q.get_down_brch(cc))
        


