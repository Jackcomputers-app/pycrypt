import os
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.getenv("DOMAIN", "localhost")

bind = "0.0.0.0:443"
workers = 4
certfile = f"/etc/letsencrypt/live/{DOMAIN}/fullchain.pem"
keyfile = f"/etc/letsencrypt/live/{DOMAIN}/privkey.pem"
