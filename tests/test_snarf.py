import os
os.environ['ENV'] = "test"
import unittest
import datetime

from OnlySnarf.util.config import config
from OnlySnarf.util import defaults as DEFAULT
from OnlySnarf.lib.driver import Driver
from OnlySnarf.util.settings import Settings
from OnlySnarf.snarf import Snarf
# from OnlySnarf.classes.user import User

today = datetime.datetime.now()
tomorrow = today + datetime.timedelta(days=1)

class TestSnarf(unittest.TestCase):

    def setUp(self):
        config["text"] = "test balls"
        Settings.set_debug("tests")
        self.test_snarf = Snarf()

    def tearDown(self):
        config["price"] = 0
        config["duration"] = None
        config["expiration"] = 0
        config["questions"] = []
        config["schedule"] = DEFAULT.SCHEDULE
        config["date"] = DEFAULT.DATE
        config["time"] = DEFAULT.TIME
        config["input"] = []
        Driver.exit()

    @unittest.skip("works")
    def test_discount(self):
        config["amount"] = DEFAULT.DISCOUNT_MAX_AMOUNT
        config["months"] = DEFAULT.DISCOUNT_MAX_MONTHS
        config["user"] = "randomficus"
        assert self.test_snarf.discount(), "unable to apply discount"
        config["amount"] = 0
        config["months"] = 0
        
    @unittest.skip("works")
    def test_message(self):
        config["input"] = ["/home/skeetzo/Projects/onlysnarf/public/images/shnarf.jpg", "/home/skeetzo/Projects/onlysnarf/public/images/snarf.jpg"]
        config["price"] = DEFAULT.PRICE_MINIMUM
        config["user"] = "randomficus"
        assert self.test_snarf.message(), "unable to send message"

    @unittest.skip("works")
    def test_post(self):
        config["input"] = ["/home/skeetzo/Projects/onlysnarf/public/images/shnarf.jpg", "/home/skeetzo/Projects/onlysnarf/public/images/snarf.jpg"]
        config["price"] = DEFAULT.PRICE_MINIMUM
        assert self.test_snarf.post(), "unable to post message"
        
    # @unittest.skip("works")
    def test_poll(self):
        config["duration"] = DEFAULT.DURATION_ALLOWED[-1]
        config["expiration"] = 999
        config["questions"] = ["suck","my","dick","please?"]
        assert self.test_snarf.post(), "unable to post poll"

    # @unittest.skip("works")
    def test_schedule(self):
        config["schedule"] = tomorrow
        config["schedule"] = config["schedule"].strftime(DEFAULT.SCHEDULE_FORMAT)
        assert self.test_snarf.post(), "unable to post schedule"
        
    # @unittest.skip("todo")
    def test_schedule_date(self):
        config["date"] = tomorrow
        config["date"] = config["date"].strftime(DEFAULT.DATE_FORMAT)
        assert self.test_snarf.post(), "unable to post schedule via date"

    # @unittest.skip("todo")
    def test_schedule_time(self):
        config["time"] = today + datetime.timedelta(hours=1)
        config["time"] = config["time"].strftime(DEFAULT.TIME_FORMAT)
        assert self.test_snarf.post(), "unable to post schedule via time"

############################################################################################

if __name__ == '__main__':
    unittest.main(warnings='ignore')