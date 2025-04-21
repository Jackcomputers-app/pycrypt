# pycrypt
 

 1. Make sure you have Python 3 install on your server. For PYcrypt to work propply yuo will need Python 3.9 or Higher.

 ```python

 python3 --version

 ```

 2. Download this repo on you computer/server.

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

6. Create a python virtual environment. 
```python

python3 -m venv venv

```
7. Enter the Python virtual environment. You will know that you are in the virtual envorment when your CLI says (.venv)
```bash

source venv/bin/activate

```

8. Install the required python dependencies
```python

pip install flask pymongo cryptography bcrypt PyJWT

```

9. Run the Bash script to set up MySQL and .env file for saying keys.
```bash

chmod +x setup.sh
./setup.sh

```

10. Next you will need to create an admin user inside the database so you can login. 

```python

python3 create_admin.py

```

11. Run and start the server. 
```python

python3 app.py

```