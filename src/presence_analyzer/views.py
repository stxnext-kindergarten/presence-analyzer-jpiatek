# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort
from flask import redirect

from flask_mako import render_template

from presence_analyzer.main import app
from presence_analyzer.utils import get_data
from presence_analyzer.utils import group_by_weekday
from presence_analyzer.utils import group_start_end
from presence_analyzer.utils import jsonify
from presence_analyzer.utils import mean

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_api(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_api(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_api(user_id):
    """
    Returns average time start-end of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)
    weekdays = group_start_end(data[user_id])

    result = [
        (calendar.day_abbr[weekday], start_end)
        for weekday, start_end in enumerate(zip(weekdays[0], weekdays[1]))
    ]
    return result


@app.route('/presence_weekday')
def presence_weekday_view():
    """
    Render template for presence weekday
    """
    return render_template('presence_weekday.html',
                           name='Presence by weekday')


@app.route('/mean_time_weekday')
def mean_time_weekday_view():
    """
    Render template for mean time weekday
    """
    return render_template('mean_time_weekday.html',
                           name='Presence mean time')


@app.route('/presence_start_end')
def presence_start_end_view():
    """
    Render template for start end
    """
    return render_template('presence_start_end.html',
                           name='Presence start-end')
