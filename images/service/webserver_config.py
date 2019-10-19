# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
from airflow import configuration as conf

basedir = os.path.abspath(os.path.dirname(__file__))

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = conf.get('core', 'SQL_ALCHEMY_CONN')

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# ----------------------------------------------------
# Authentication Configuration
# ----------------------------------------------------

# When using airflow.api.auth.backend.default

# from flask_appbuilder.security.manager import AUTH_DB
# AUTH_TYPE = AUTH_DB
# AUTH_USER_REGISTRATION = True
# AUTH_USER_REGISTRATION_ROLE = "Admin"

# When using Google OAuth Auth

# from flask_appbuilder.security.manager import AUTH_OAUTH
# AUTH_TYPE = AUTH_OAUTH
# AUTH_USER_REGISTRATION = True
# AUTH_USER_REGISTRATION_ROLE = "Admin"

# OAUTH_PROVIDERS = [{
# 	'name':'google',
#     'whitelist': [
#         SOME_EMAIL_DOMAIN # '@example.com'
#     ],
#     'token_key':'access_token',
#     'icon':'fa-google',
#         'remote_app': {
#             'base_url':'https://www.googleapis.com/oauth2/v2/',
#             'request_token_params':{
#                 'scope': 'email profile'
#             },
#             'access_token_url':'https://accounts.google.com/o/oauth2/token',
#             'authorize_url':'https://accounts.google.com/o/oauth2/auth',
#             'request_token_url': None,
#             'consumer_key': SOME_KEY
#             'consumer_secret': SOME_SECRET
#         }
# }]

# ----------------------------------------------------
# Theme CONFIG
# ----------------------------------------------------
# Flask App Builder comes up with a number of predefined themes
# that you can use for Apache Airflow.
# http://flask-appbuilder.readthedocs.io/en/latest/customizing.html#changing-themes
# Please make sure to remove "navbar_color" configuration from airflow.cfg
# in order to fully utilize the theme. (or use that property in conjunction with theme)
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
