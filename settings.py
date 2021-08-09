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
        1. Show roster
        2. Add contact
        3. Show contact details
        4. Send direct message
        5. Change presence
        6. Start groupchat
        7. Logout
        8. Delete my account
        9. Exit
"""