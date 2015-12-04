# coding=utf-8
# Created 2014 by Janusz Skonieczny 

import logging
import os

SRC_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# ============================================================================
#  a flask settings
#  http://flask.pocoo.org/docs/config/#configuring-from-files
# ============================================================================

SECRET_KEY = '47e585de7f22984d5ee291c2f31412384bfc32d0'
FLASH_MESSAGES = True

# Flask-SQLAlchemy
# http://pythonhosted.org/Flask-SQLAlchemy/config.html

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SRC_DIR, "db.sqlite")
SQLALCHEMY_ECHO = False  # Doubles log statements, investigate
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Login
# https://flask-login.readthedocs.org/en/latest/#protecting-views

LOGIN_DISABLED = False

# Flask-Security
# http://pythonhosted.org/Flask-Security/configuration.html

SECURITY_PASSWORD_SALT = "abc"
# SECURITY_PASSWORD_HASH = "bcrypt"  # requires py-bcrypt
# SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_HASH = "plaintext"
SECURITY_EMAIL_SENDER = "support@example.com"

SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True

SECURITY_CONFIRM_SALT = "570be5f24e690ce5af208244f3e539a93b6e4f05"
SECURITY_REMEMBER_SALT = "de154140385c591ea771dcb3b33f374383e6ea47"
SECURITY_DEFAULT_REMEMBER_ME = True

# Set secret keys for CSRF protection
CSRF_SESSION_KEY = '8a7474974efcf76896aa84eea9cbe016bbc08828'
CSRF_ENABLED = True

# Flask-Babel
# http://pythonhosted.org/Flask-Babel/
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"

# Flask-Mail
# http://pythonhosted.org/Flask-Mail/
SERVER_EMAIL = 'Flask-SocialBlueprint <support@example.com>'

from local_settings import *
