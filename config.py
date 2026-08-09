from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
ADMIN_ID = int(getenv("ADMIN_ID"))