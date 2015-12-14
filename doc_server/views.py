import cPickle as pickle
import os

import flask
from flask import Blueprint, current_app, render_template, make_response
from flask_login import login_required
from hotdoc.core.doc_tool import DocTool
from flask.views import MethodView, View
from flask_login import current_user
from flask_restful import abort

from patcher import Patcher

from datetime import datetime

# This causes errors on the atexit thread when run under mod_wsgi
# Seemingly related : https://github.com/ipython/ipython/issues/680
from IPython.core.history import HistoryManager
HistoryManager.enabled = False

class MyBlueprint(Blueprint):
    def get_send_file_max_age(self, name):
        if name.endswith('.html'):
            return 0
        return Blueprint.get_send_file_max_age(self, name)

app = MyBlueprint("doc_server", __name__, template_folder="templates")

class RawCommentAPI(MethodView):
    @login_required
    def get(self, symbol_id):
        sym = doc_tool.get_symbol(symbol_id)
        if sym:
            return sym.comment.raw_comment

        abort(make_response('No such symbol %s' % symbol_id, 404))

    @login_required
    def put(self, symbol_id):
        raw_comment = flask.request.form.get('raw_comment')
        sym = doc_tool.get_symbol(symbol_id)

        language = flask.request.args.get('language')
        if language is not None:
            gi_extension = doc_tool.extensions['gi-extension']
            gi_extension.setup_language(language)

        if not sym:
            abort(make_response('No such symbol %s' % symbol_id, 404))

        comment = doc_tool.raw_comment_parser.parse_comment(raw_comment,
                'nowhere', 0, 0)

        if not comment:
            abort(make_response('Invalid comment', 400))

        if comment.name != sym.unique_name:
            abort(make_response('Can not change the name of a comment', 400)) 

        old_comment = sym.comment
        sym.comment = comment
        res = doc_tool.format_symbol(symbol_id)
        sym.comment = old_comment

        return res


class PublishAPI(MethodView):
    @login_required
    def post(self, symbol_id):
        n = datetime.now()
        raw_comment = flask.request.form.get('raw_comment')
        message = flask.request.form.get('message')
        if not message:
            message = 'Online edit'

        raw_comment = '\n'.join(l.rstrip() for l in raw_comment.strip().split('\n'))
        sym = doc_tool.get_symbol(symbol_id)
        old_comment = sym.comment

        if not sym:
            abort(make_response('No such symbol %s' % symbol_id, 404))

        if raw_comment == sym.comment.raw_comment:
            abort(make_response('You did not make any changes', 400))

        if not doc_tool.patch_page(sym, raw_comment):
            abort(make_response("Couldn't patch documentation", 400))

        patcher.patch(old_comment.filename,
                old_comment.lineno - 1,
                old_comment.endlineno, raw_comment + '\n')

        patcher.add(sym.comment.filename)
        name = "Online user"
        if current_user.first_name and current_user.last_name:
            name = '%s %s' % (current_user.first_name, current_user.last_name)

        patcher.commit(name, current_user.email, message)
        language = flask.request.args.get('language', '')
        ref = os.path.join(doc_tool.editing_server, 'static',
                os.path.basename(doc_tool.output), language, sym.link.ref)
        return ref

class FormattedCommentAPI(MethodView):
    @login_required
    def get(self, symbol_id):
        return doc_tool.format_symbol(symbol_id)

class RenderTemplateView(View):
    def __init__(self, template_name):
        self.template_name = template_name

    @login_required
    def dispatch_request(self, symbol_id):
        base_url = '..'
        language = flask.request.args.get("language", '')

        # Need a terminating slash
        base_url = os.path.join('/', 'static', 'html', language, '')
        return render_template(self.template_name, symbol_id=symbol_id,
                address=doc_tool.editing_server, base_url=base_url,
                language=language)

def do_format(args):
    global patcher
    global doc_tool

    if not doc_tool:
        doc_tool = DocTool()
    doc_tool.setup(args)
    if not patcher:
        patcher = Patcher(doc_tool.git_repo_path)

    modpath = os.path.dirname(__file__)
    output = os.path.join(modpath, '..', 'static', 'html')
    doc_tool.output = output
    doc_tool.format()

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
