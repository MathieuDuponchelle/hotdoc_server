# coding=utf-8
# Created 2014 by Janusz Skonieczny
import os
import sys
from hotdoc.utils.utils import load_all_extensions

SRC_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_FOLDER = os.path.join(SRC_DIR, "templates")
STATIC_FOLDER = os.path.join(SRC_DIR, "static")

import flask_social_blueprint

from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__, template_folder=TEMPLATE_FOLDER,
        static_folder=STATIC_FOLDER)
CORS(app)

# -------------------------------------------------------------
# Load settings from separate modules
# -------------------------------------------------------------

import website.settings
app.config.from_object(website.settings)

# -------------------------------------------------------------
# Custom add ons
# -------------------------------------------------------------

from website.database import db
db.init_app(app)

# Enable i18n and l10n
from flask_babel import Babel
babel = Babel(app)

# Authentication
import auth.models
auth.models.init_app(app)

import auth.views
app.register_blueprint(auth.views.app)

# Doc service
import doc_server.views
app.register_blueprint(doc_server.views.app)

# -------------------------------------------------------------
# Development server setup
# -------------------------------------------------------------

@app.route('/<path:path>')
def static_proxy(path):
    try:
        res = app.send_static_file(path)
    except Exception as e:
        print "error while serving static", e

def setup_doc_server(args):
    # Setup our initial pages
    print "loading extensions"
    load_all_extensions()
    print "formatting"
    doc_server.views.do_format(args)

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    doc_server.views.doc_tool.finalize()

if __name__ == "__main__":
    # for convenience in setting up OAuth ids and secretes we use the example.com domain.
    # This should allow you to circumvent limits put on localhost/127.0.0.1 usage
    # Just map dev.example.com on 127.0.0.1 ip address.
    setup_doc_server(sys.argv[1:])
    app.run(host="0.0.0.0", port=5055)
