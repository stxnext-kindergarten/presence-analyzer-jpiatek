# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""

from flask import Flask
from flask_mako import MakoTemplates


app = Flask(  # pylint: disable=invalid-name
    __name__, template_folder="templates")
mako = MakoTemplates(app)  # pylint: disable=invalid-name

app.config.from_object('config')
