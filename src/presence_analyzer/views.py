# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging

from flask import abort
from flask import redirect

from flask_mako import render_template

from operator import itemgetter

from presence_analyzer.main import app
from presence_analyzer.utils import get_data
from presence_analyzer.utils import group_by_weekday
from presence_analyzer.utils import group_start_end
from presence_analyzer.utils import jsonify
from presence_analyzer.utils import mean
from presence_analyzer.utils import get_users
from presence_analyzer.utils import get_server


log = logging.getLogger(__name__)  # pylint: disable=invalid-name
HOST = get_server()


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
    users = get_users()

    id_username_list = [
        {'user_id': i, 'name': users[i].get('name')}
        for i in users.keys()]
    sorted_by_username = sorted(id_username_list, key=itemgetter('name'))
    return sorted_by_username


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


@app.route('/api/v1/get_url_photo/<int:user_id>', methods=['GET'])
@jsonify
def get_url_photo(user_id):
    """
    Returns url for user photo
    """

    users = get_users()
    if user_id not in users.keys():
        log.debug('User %s not found!', user_id)
        abort(404)
    return {'url': HOST + users[user_id].get('avatar')}


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
