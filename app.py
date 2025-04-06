from flask import Flask, request, jsonify
from pymongo import MongoClient
from cryptography.fernet import Fernet
from bson.objectid import ObjectId
import jwt, datetime
from functools import wraps
import bcrypt

app = 