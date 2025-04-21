#!/bin/bash

#Setup MySQL on the server. 
echo "Updating packages..."
sudo apt update

echo "Installing MySQL Server..."
sudo apt install -y mysql-server

echo "Starting MySQL service..."
sudo systemctl start mysql
sudo systemctl enable mysql

echo "Creating database and user..."

sudo mysql <<EOF

-- Create database
CREATE DATABASE IF NOT EXISTS pycrypt;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'pycryptuser'@'localhost' IDENTIFIED BY 'StrongPassword123';
GRANT ALL PRIVILEGES ON pycrypt.* TO 'pycryptuser'@'localhost';
FLUSH PRIVILEGES;

-- Create users table
USE pycrypt;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'sender', 'receiver') NOT NULL
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(100),
    receiver VARCHAR(100),
    message TEXT
);

EOF

#Part to make .env file for server. 
echo "Generating Flask secret and Fernet key..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
FLASK_SECRET=$(python3 -c "import os; print(os.urandom(24).hex())")

echo "Writing .env file..."
cat > $ENV_FILE <<EOF
FLASK_SECRET=$FLASK_SECRET
FERNET_KEY=$FERNET_KEY
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_NAME=$DB_NAME
DB_HOST=localhost
EOF

echo "MySQL and .env setup complete!"