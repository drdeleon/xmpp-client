# settings.py
import os
import logging

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Environment variables
JID = os.environ.get("JID")
PASSWORD = os.environ.get("PASSWORD")
DEBUG = os.environ.get("DEBUG").lower()=='true'

# Logging
log_lvl = logging.DEBUG if DEBUG else logging.ERROR
logging.basicConfig(
    level=log_lvl,
    format='%(levelname)-8s %(message)s'
)

# Constants
INIT_MENU = """
    -------------------------------
                WELCOME
    -------------------------------
        1. Registration
        2. Login
        3. Exit
"""

MAIN_MENU = """
    -------------------------------
                MAIN MENU
    -------------------------------
        1. Add contact
        2. Show contact details
        3. Send direct message
        4. Change presence
        5. Start groupchat
        6. Logout
        7. Delete my account
        8. Exit
"""