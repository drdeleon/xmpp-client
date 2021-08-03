# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

JID = os.environ.get("JID")
PASSWORD = os.environ.get("PASSWORD")

print(JID)
print(PASSWORD)