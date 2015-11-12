import cPickle as pickle
import os, sys

import flask
from flask import Blueprint, current_app, render_template
from flask_login import login_required
from hotdoc.core.doc_tool import DocTool
from hotdoc.utils.utils import load_all_extensions
from flask.views import MethodView, View

from patcher import Patcher

app = Blueprint("doc_server", __name__, template_folder="templates")

class RawCommentAPI(MethodView):
    def get(self, symbol_id):
        sym = doc_tool.get_symbol(symbol_id)
        if sym:
            return sym.comment.raw_comment
        return ''

    def put(self, symbol_id):
        raw_comment = flask.request.form.get('raw_comment')
        sym = doc_tool.get_symbol(symbol_id)
        if not sym:
            return ''

        comment = doc_tool.raw_comment_parser.parse_comment(raw_comment,
                'nowhere', 0, 0)

        old_comment = sym.comment
        sym.comment = comment
        res = doc_tool.format_symbol(symbol_id)
        sym.comment = old_comment

        return res


class PublishAPI(MethodView):
    def post(self, symbol_id):
        raw_comment = flask.request.form.get('raw_comment')
        message = flask.request.form.get('message')
        if not message:
            message = 'Online edit'

        raw_comment = '\n'.join(l.rstrip() for l in raw_comment.split('\n')) + '\n'
        sym = doc_tool.get_symbol(symbol_id)
        patcher.patch(sym.comment.filename,
                sym.comment.lineno - 1,
                sym.comment.endlineno, raw_comment)

        patcher.add(sym.comment.filename)
        patcher.commit('meh', 'meh@meh.net', message)
        ref = os.path.join(doc_tool.output, 'c', sym.link.ref)
        do_format()
        return '/%s' % ref

class FormattedCommentAPI(MethodView):
    def get(self, symbol_id):
        return doc_tool.format_symbol(symbol_id)

class RenderTemplateView(View):
    def __init__(self, template_name):
        self.template_name = template_name

    def dispatch_request(self, symbol_id):
        return render_template(self.template_name, symbol_id=symbol_id)


def do_format():
    global patcher
    global doc_tool

    if not patcher:
        patcher = Patcher(sys.argv[2])
    if not doc_tool:
        doc_tool = DocTool()
    hd_args = pickle.load(open(os.path.join(sys.argv[1], 'args.p'), 'rb'))
    doc_tool.setup(hd_args)
    doc_tool.output = 'static/html'
    doc_tool.format()
    # FIXME: let's be more clever at some point
    gi_extension = doc_tool.extensions['gi-extension']
    gi_extension.setup_language('c')


patcher = None
doc_tool = None

raw_comment_view = RawCommentAPI.as_view('raw_comment_api')
app.add_url_rule('/raw_comments/<symbol_id>', view_func=raw_comment_view,
                         methods=['GET', 'PUT'])

formatted_comment_view = FormattedCommentAPI.as_view('formatted_comment_api')
app.add_url_rule('/formatted_comments/<symbol_id>', view_func=formatted_comment_view,
                         methods=['GET'])

publish_view = PublishAPI.as_view('publish_api')
app.add_url_rule('/publish/<symbol_id>', view_func=publish_view,
                         methods=['POST'])

app.add_url_rule('/editor/<symbol_id>',
        view_func=RenderTemplateView.as_view('edit_page',
            template_name='edit_page.html'))
