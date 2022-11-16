import os

BOT_TOKEN = os.environ.get("BOT_TOKEN") or None
AUTHORITY_TOKEN = os.environ.get("AUTHORITY_TOKEN") or "autoken"
URL = os.environ.get("URL") or "http://localhost:1423/api/"