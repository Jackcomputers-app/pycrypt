from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from cryptography.fernet import Fernet
import jwt, datetime, os, bcrypt
from functools import wraps
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
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


# If MySQL connection fail this script will try the connection again.
def ensure_db_connection():
    global db, cursor
    try:
        db.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as e:
        print(f"Database connection lost: {e}. Trying to reconnect...")
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
def get_messages_by_user(username):
    if not db.is_connected():
        db.reconnect()

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM messages WHERE sender=%s OR receiver=%s",
        (username, username)
    )
    return cursor.fetchall()



# Routes in html
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

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT sender, receiver, message FROM messages
        WHERE sender = %s OR receiver = %s
    """, (username, username))

    raw = cursor.fetchall()
    messages = []
    for row in raw:
        contact = row['receiver'] if row['sender'] == username else row['sender']
        messages.append({
            'contact': contact,
            'message': row['message']
        })

    title = "Your Messages"

    
    decrypted = []
    for row in messages:
        try:
            decrypted.append({
                'with': row['contact'],
                'message': fernet.decrypt(row['message'].encode()).decode()
            })
        except Exception as e:
            decrypted.append({
                'with': row['contact'],
                'message': "[Unable to decrypt]"
            })

    return render_template('dashboard.html', messages=decrypted, title=title)


DOMAIN = os.getenv("DOMAIN", "localhost")

if __name__ == "__main__":
    print("The app has loaded. Please note you will need to use guncorn to run the app itself. Run the ./start.sh file to start the server.")

if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/server.log', maxBytes=10240, backupCount=5)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)