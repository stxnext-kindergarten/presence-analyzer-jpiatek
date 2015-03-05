# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import json
import os.path
import unittest

from presence_analyzer import views  # pylint: disable=unused-import
from presence_analyzer import main
from presence_analyzer import utils
from presence_analyzer.utils import interval
from presence_analyzer.utils import mean
from presence_analyzer.utils import seconds_since_midnight

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):

    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test mean presence time of given user grouped by weekday.
        """

        bad_url = '/api/v1/mean_time_weekday/%s' % '9'
        good_url = '/api/v1/mean_time_weekday/%s' % '11'
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(good_url)
        self.assertEqual(resp.status_code, 200)

    def test_presence_weekday_view(self):
        """
        Test total presence time of given user grouped by weekday.
        """
        bad_url = '/api/v1/presence_weekday/%s' % '9'
        good_url = '/api/v1/presence_weekday/%s' % '11'
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(good_url)
        self.assertEqual(resp.status_code, 200)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):

    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_mean(self):
        """
        Test calculating mean
        """
        self.assertEqual(mean([29272, 29680, 86112]), 48354.666666666664)
        self.assertEqual(mean([]), 0)
        self.assertIsInstance(mean([29272, 29680, 86112]), float)

    def test_seconds_since_midnight(self):
        """
        Test calculating amount of seconds since midnight.
        """
        self.assertEqual(seconds_since_midnight(datetime.time(2, 39, 1)), 9541)
        self.assertEqual(seconds_since_midnight(datetime.time(0, 0, 0)), 0)
        self.assertEqual(
            seconds_since_midnight(datetime.time(23, 59, 59)), 86399)
        self.assertNotEqual(
            seconds_since_midnight(datetime.time(1, 12, 59)), 0)

    def test_interval(self):
        """
        Test calculating inverval in seconds between two datetime.time objects.
        """
        self.assertEqual(
            interval(datetime.time(8, 0, 0), datetime.time(16, 0, 0)), 28800
        )
        self.assertEqual(
            interval(datetime.time(8, 0, 0), datetime.time(8, 0, 0)), 0
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
