from flask import Blueprint, current_app, render_template
from flask_login import login_required
from hotdoc.core.doc_tool import DocTool
from hotdoc.utils.utils import load_all_extensions

app = Blueprint("doc_server", __name__, template_folder="templates")

load_all_extensions()
doc_tool = DocTool()

@app.route("/symbols/")
@login_required
def profile():
    return 'You should be logged in I hope'
