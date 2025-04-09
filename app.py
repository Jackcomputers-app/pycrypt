from flask import Flask, request, jsonify
from pymongo import MongoClient
from cryptography.fernet import Fernet
from bson.objectid import ObjectId
import jwt, datetime
from functools import wraps
import bcrypt


# Templates are handled and pulled in the scirpt.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
Fernet_KEY = Fernet.generate_key()
fernet = Fernet(Fernet_KEY)

# MongoDB connection using SCRAM
