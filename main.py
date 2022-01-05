from flask import Flask, jsonify, request, session, make_response, render_template
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JustDemonstrating'

def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Missing token'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    if not session.get('logged in'):
        return render_template('login.html')
    else:
        return 'Currently logged in'

@app.route('/public')
def public():
    return 'Anyone can view this'

@app.route('/auth')
@check_for_token
def authorized():
    return 'This is only viewable with a token'

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] and request.form['password'] == 'password':
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
        },
        app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "login" '})

if __name__ == '__main__':
    app.run(debug=True)