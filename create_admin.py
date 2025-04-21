import mysql.connector
import bcrypt
import getpass
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pycrypt")
DB_USER = os.getenv("DB_USER", "pycryptuser")
DB_PASS = os.getenv("DB_PASS", "StrongPassword123")

print("It's time to create an Admin User")
username = input("Enter admin username: ").strip()
while not username:
    username = input("You did not give me a username. You need to give me a username otherwise you will have a badtime with the program.")

password = getpass.getpass("Enter admin Password:")
confirm = getpass.getpass

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = db.cursor()

    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin')",
        (username, hashed)
    )
    db.commit()
    print(f"Admin user '{username}' created successfully.")
except Exception as e:
    print("Error:", e)
finally:
    if'db' in locals() and db.is_connected();
        cursor.close()
        db.close()