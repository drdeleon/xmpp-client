import settings
import sys
from getpass import getpass

from xmpp_client import Client


xmpp = None


def main():
    RUNNING = True

    while(RUNNING):
        print(settings.INIT_MENU)
        init_option = int(input("\nSelect an option: "))

        if init_option==1: # Registration 

            jid = str(input("JID: "))
            pwd = str(getpass("Password: "))

            if "@alumchat.xyz" in jid:
                xmpp = Client(jid, pwd)
            else:
                jid = jid + "@alumchat.xyz"
                xmpp = Client(jid, pwd)

            xmpp.connect()
            xmpp.process()

            IN_APP_LOOP = True

            while IN_APP_LOOP:
                print(settings.MAIN_MENU)
                menu_option = int(input("\nSelect an option: "))
                app(menu_option)
            
            pass

        if init_option==2: # Login 

            jid = str(input("JID: "))
            pwd = str(getpass("Password: "))

            xmpp = Client(jid, pwd)

            xmpp.connect()
            xmpp.process()

            IN_APP_LOOP = True

            while IN_APP_LOOP:
                print(settings.MAIN_MENU)
                menu_option = int(input("\nSelect an option: "))
                app(menu_option)

            pass

        if init_option == 3: # Exit 
            print("Goodbye!")
            sys.exit()


def app(option:int):
    
    if option==1: # Add contact
        pass

    elif option==2: # Show contact details
        pass

    elif option==3: # Send direct message
        pass

    elif option==4: # Change presence
        pass

    elif option==5: # Groupchat
        pass

    elif option==6: # Logout
        pass

    elif option==7: # Delete my account
        pass

    elif option==8: # Exit
        print("Goodbye!")
        sys.exit()

    else:
        print("Enter a valid option.")
    


if __name__ == "__main__":
    main()