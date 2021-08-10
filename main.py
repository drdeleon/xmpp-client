import logging

from aioconsole.stream import ainput
import settings
import sys
import threading
import asyncio
from getpass import getpass

from slixmpp.exceptions import IqTimeout

from register_account import RegisterBot
from xmpp_client import Client


xmpp = None


def main():
    RUNNING = True

    while(RUNNING):
        print(settings.INIT_MENU)
        try:
            init_option = int(input("\nSelect an option: "))
        except EOFError:
            return

        if init_option==1: # Registration 

            if settings.JID and settings.PASSWORD:
                jid, pwd = settings.JID, settings.PASSWORD
            else:
                jid = str(input("JID: "))
                pwd = str(getpass("Password: "))

            if "@alumchat.xyz" not in jid:
                jid = jid + "@alumchat.xyz"

            xmpp = RegisterBot(jid, pwd)

            xmpp['xep_0077'].force_registration = True

            xmpp.connect()
            xmpp.process(forever=False)

            xmpp = None


        if init_option==2: # Login 

            if settings.JID and settings.PASSWORD:
                jid, pwd = settings.JID, settings.PASSWORD
            else:
                jid = str(input("JID: "))
                pwd = str(getpass("Password: "))

            xmpp = Client(jid, pwd)

            xmpp.connect()
            xmpp.process(forever=False)


        if init_option == 3: # Exit 
            print("Goodbye!")
            sys.exit()

    


if __name__ == "__main__":
    main()