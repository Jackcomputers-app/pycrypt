# PYcrypt
 

 1. Make sure you have Python 3 installed on your server. For PYcrypt to work properly, you will need Python 3.9 or higher. This Documentation is written for python 3.12

 ```python
 python3 --version
 ```

 2. Download this repo on your computer/server.

 ```bash
 wget https://github.com/Jackcomputers-app/pycrypt/archive/refs/heads/main.zip
 ```

 3. Run sudo apt update and install an unzip tool
```bash
sudo apt update
sudo apt install unzip
```

4. Unzip the folder
```bash
unzip main.zip
```
5. Move into the directory
```bash
cd pycrypt-main
```

6. Install the Python virtual envioment toolkit for your version of Python. 
```bash
sudo apt install python3.12-venv
```

7. Create a python virtual environment. 
```python
python3 -m venv venv
```
8. Enter the Python virtual environment. You will know that you are in the virtual environment when your CLI says (.venv)
```bash
source venv/bin/activate
```

9. Install the required python dependencies
```python
pip install flask pymongo cryptography bcrypt PyJWT mysql-connector-python python-dotenv gunicorn
```

10. Run the Bash script to set up MySQL and .env file for saying keys.
```bash
chmod +x setup.sh
./setup.sh
```

11. Next you will need to create an admin user inside the database so you can login to the website.

```bash
python3 create_admin.py
```

12. Install certbot to request an SSL certificate for your domain name. 
```bash
sudo apt install certbot
```

13. Enable SSL(Secure Socket Layer) on your webserver. Replace pycrypt.jackcomputers.app with your Domain name. 
```bash
sudo certbot certonly --standalone -d pycrypt.jackcomputers.app
```

14. Run change the Permissions of start.sh and start the web server. 
```bash
chmod +x start.sh
./start.sh
```