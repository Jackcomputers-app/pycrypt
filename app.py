from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from cryptography.fernet import Fernet
import jwt, datetime, os, bcrypt
from functools import wraps
from dotenv import load_dotenv
print(Fernet.generate_key().decode())




load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'dev-secret')
app.secret_key = app.config['SECRET_KEY']

# Fernet key for encrypting messages
fernet_key = os.getenv("FERNET_KEY", Fernet.generate_key().decode()).encode()
fernet = Fernet(fernet_key)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="pycryptuser",
    password="StrongPassword123",
    database="pycrypt"
)
cursor = db.cursor(dictionary=True)

def token_required(roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = session.get('token')
            if not token:
                return redirect(url_for('login'))
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                if roles and data['role'] not in roles:
                    return "Unauthorized", 403
                request.user = data
            except jwt.ExpiredSignatureError:
                session.pop('token', None)
                return redirect(url_for('login'))
            except Exception:
                session.pop('token', None)
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(data['password'].encode(), user['password'].encode()):
            return render_template('login.html', error='Invalid credentials')

        token = jwt.encode({
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        session['token'] = token
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def register_user():
    if request.method == 'POST':
        data = request.form
        cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        if cursor.fetchone():
            return render_template('register.html', error='User already exists')

        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (data['username'], hashed, data['role']))
        db.commit()
        return render_template('register.html', success='User registered successfully')

    return render_template('register.html')


@app.route('/send', methods=['GET', 'POST'])
@token_required(roles=['sender', 'admin'])
def send_message():
    prefill_to = request.args.get('to', '')

    if request.method == 'POST':
        payload = request.form
        encrypted = fernet.encrypt(payload['message'].encode()).decode()
        cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)",
                       (request.user['username'], payload['to'], encrypted))
        db.commit()
        return render_template('send.html', success='Message sent')

    return render_template('send.html', prefill_to=prefill_to)


@app.route('/dashboard')
@token_required()
def dashboard():
    username = request.user['username']
    role = request.user['role']

    if role == 'sender':
        cursor.execute("SELECT receiver AS `with`, message FROM messages WHERE sender = %s", (username,))
        title = "Messages You've Sent"
    elif role == 'receiver':
        cursor.execute("SELECT sender AS `with`, message FROM messages WHERE receiver = %s", (username,))
        title = "Messages You've Received"
    elif role == 'admin':
        cursor.execute("SELECT sender AS `with`, message FROM messages")
        title = "All Messages in System"
    else:
        return "Role not authorized", 403

    rows = cursor.fetchall()
    messages = [{
        'with': row['with'],
        'message': fernet.decrypt(row['message'].encode()).decode()
    } for row in rows]

    return render_template('dashboard.html', messages=messages, title=title)

if __name__ == '__main__':
    app.run(debug=True)
