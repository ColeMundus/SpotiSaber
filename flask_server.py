from flask import Flask, request
import logging
import sys
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def arg_parse():
    print(request.url)
    global auth
    auth = {
        'access_token': request.args.get('access_token'),
        'token_type': request.args.get('token_type'),
        'expires_in': request.args.get('expires_in'),
        'state': request.args.get('state')
    }
    shutdown_server()
    response = "Please refer back to application"
    return response

def get_cred():
    app.run()
    return auth
