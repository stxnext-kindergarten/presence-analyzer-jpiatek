# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import logging
from datetime import datetime
from functools import wraps
from json import dumps

from flask import Response
from lxml import etree

from presence_analyzer.main import app

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
TREE = etree.parse(app.config['DATA_XML'])  # pylint: disable=no-member


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def get_users_from_xml():
    """
    Extracts users data from xml file. Returns dict.
    It creates structure like this:
    {'151': {'avatar': '/api/images/users/151', 'name': 'Dawid J.'}}
    """

    users_data = {}
    for element in TREE.iter('user'):
        users_data[element.get('id')] = {
            'avatar': element[0].text, 'name': element[1].text}
    return users_data


def get_users():
    """
    Comparing lists ID's extracted from xml file and csv.
    If ID from CSV file is not in XML file adding default values.
    Structure of dict is below:

    {'151': {'avatar': '/api/images/users/151', 'name': 'Dawid J.'},
    18: {'avatar': '/api/images/users/00', 'name': 'User 18'}}
    """

    out = {}
    data = get_data()
    users = get_users_from_xml()
    for i in data.keys():
        user = users.get(str(i))
        if user:
            out[i] = user
        else:
            out[i] = {
                'avatar': '/api/images/users/00', 'name': 'User {0}'.format(i)}
    return out


def get_server():
    """
    Extracts hostname and protocol data from xml file. Returns string.
    """
    host = TREE.find('server')[2].text
    protocol = TREE.find('server')[0].text
    return '{0}://{1}'.format(host, protocol)


def seconds_to_time(seconds):
    """
    Calculate time HH:MM:SS from seconds since midnight
    """
    minuts, seconds = divmod(seconds, 60)
    hours, minuts = divmod(minuts, 60)
    hms = "%d:%02d:%02d" % (hours, minuts, seconds)
    return hms


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_start_end(items):
    """
    Caclulate average start end by weekday. Returns tuple with two lists
    """
    result_starts = [[], [], [], [], [], [], []]
    result_ends = [[], [], [], [], [], [], []]

    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result_starts[date.weekday()].append(seconds_since_midnight(start))
        result_ends[date.weekday()].append(seconds_since_midnight(end))
    result_starts = [
        seconds_to_time(mean(x)) if len(x) > 0 else x for x in result_starts]
    result_ends = [
        seconds_to_time(mean(x)) if len(x) > 0 else x for x in result_ends]
    return result_starts, result_ends


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
