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
from presence_analyzer.cron import fetch_xml_file
from presence_analyzer.utils import cache
from presence_analyzer.utils import get_data
from presence_analyzer.utils import get_users
from presence_analyzer.utils import group_start_end
from presence_analyzer.utils import interval
from presence_analyzer.utils import mean
from presence_analyzer.utils import seconds_since_midnight

from time import time as timer


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.xml'
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
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(data[0], {u'user_id': 11, u'name': u'Maciej D.'})

    def test_mean_time_weekday_api(self):
        """
        Test mean presence time of given user grouped by weekday.
        """

        bad_url = '/api/v1/mean_time_weekday/%s' % '9'
        good_url = '/api/v1/mean_time_weekday/%s' % '11'
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(good_url)
        self.assertEqual(resp.status_code, 200)

    def test_presence_weekday_api(self):
        """
        Test total presence time of given user grouped by weekday.
        """
        bad_url = '/api/v1/presence_weekday/%s' % '9'
        good_url = '/api/v1/presence_weekday/%s' % '11'
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(good_url)
        self.assertEqual(resp.status_code, 200)

    def test_presence_start_end_api(self):
        """
        Test average time start-end of given user grouped by weekday.
        """
        bad_url = '/api/v1/presence_start_end/%s' % '9'
        good_url = '/api/v1/presence_start_end/%s' % '11'
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(good_url)
        self.assertEqual(resp.status_code, 200)

    def test_presence_weekday_view(self):
        """
        Test presence weekday view
        """
        resp = self.client.get('/presence_weekday')
        self.assertEqual(resp.status_code, 200)

    def test_mean_time_weekday_view(self):
        """
        Test mean time weekday view
        """
        resp = self.client.get('/mean_time_weekday')
        self.assertEqual(resp.status_code, 200)

    def test_presence_start_end_view(self):
        """
        Test presence start end_ wiew
        """
        resp = self.client.get('/presence_start_end')
        self.assertEqual(resp.status_code, 200)

    def test_get_url_photo(self):
        """
        Test url photo
        """
        resp = self.client.get('/api/v1/get_url_photo/999')
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get('/api/v1/get_url_photo/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.data,
            '{"url": "https://intranet.stxnext.pl/api/images/users/10"}'
        )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):

    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11, 37])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_users_from_xml(self):
        """
        Test extracting data from xml file
        """
        users = get_users()
        self.assertEqual(
            users.get(11),
            {'avatar': '/api/images/users/11', 'name': 'Maciej D.'})

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

    def test_group_start_end(self):
        """
        Test calculating average start stop presence
        """
        data = get_data()
        self.assertEqual(group_start_end(data[11])[0][1], '9:19:50')
        self.assertEqual(len(group_start_end(data[11])), 2)
        self.assertEqual(group_start_end(
            data[10])[0], [[], '9:39:05', '9:19:52', '10:48:46', [], [], []])

    def test_cache(self):
        """
        Cache Tests
        """

        def dummy_func():
            """
            Returns get_data()
            """

            return get_data()

        test_obj = cache(600)
        self.assertEqual(test_obj.mem, {})
        self.assertEqual(dummy_func(), get_data())


class PresenceAnalyzerCronTestCase(unittest.TestCase):

    """
    Cron tests
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        self.client = main.app.test_client()
        self.url = 'http://sargo.bolt.stxnext.pl/users.xml'

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_cron(self):
        """
        Cron tests
        """
        self.assertEqual(fetch_xml_file(self.url), 'OK')
        self.assertFalse(fetch_xml_file(self.url + '11'))


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerCronTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
