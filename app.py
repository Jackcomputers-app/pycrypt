from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from cryptography.fernet import Fernet
from bson.objectid import ObjectId
import jwt, datetime
from functools import wraps
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Use env variable in production
fernet_key = Fernet.generate_key()
fernet = Fernet(fernet_key)

# MongoDB Connection (SCRAM Authentication)
client = MongoClient("mongodb://admin:secureAdminPass@localhost:27017/?authSource=secure_messaging")
db = client.secure_messaging
users = db.users
messages = db.messages

# Used for checking user token and role verficaton
def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = session.get('token')
            if not token:
                return redirect(url_for('login_form'))
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                if role and data['role'] != role:
                    return "Unauthorized", 403
                request.user = data
            except:
                return "Invalid or expired token", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
@token_required(role='admin')
def register_user():
    if request.method == 'POST':
        data = request.form
        if users.find_one({'username': data['username']}):
            return render_template('register.html', error='User already exists')

        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
        users.insert_one({
            'username': data['username'],
            'password': hashed,
            'role': data['role']
        })
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = users.find_one({'username': data['username']})
        if not user or not bcrypt.checkpw(data['password'].encode(), user['password']):
            return render_template('login.html', error='Invalid credentials')

        token = jwt.encode({
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        session['token'] = token
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/send', methods=['GET', 'POST'])
@token_required(role='sender')
def send_message():
    if request.method == 'POST':
        payload = request.form
        encrypted = fernet.encrypt(payload['message'].encode())
        messages.insert_one({
            'from': request.user['username'],
            'to': payload['to'],
            'message': encrypted
        })
        return render_template('send.html', success='Message sent')
    return render_template('send.html')

@app.route('/messages')
@token_required(role='receiver')
def get_messages():
    received = messages.find({'to': request.user['username']})
    output = [{
        'from': m['from'],
        'message': fernet.decrypt(m['message']).decode()
    } for m in received]
    return render_template('messages.html', messages=output)

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'another-secret-key'
    app.run(debug=True)
