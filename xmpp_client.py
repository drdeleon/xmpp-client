
import asyncio
import logging
from re import L, M
import settings
import sys

import slixmpp
from slixmpp.exceptions import IqError, IqTimeout, XMPPError
from aioconsole import ainput


def clean_jid(jid, domain="@alumchat.xyz"):
    if jid[-13:] != domain:
        jid += domain
    
    return jid


class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.nick = None

        # PLUGINS
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0085') # Chat State Notifications
        self.register_plugin('xep_0077') # In-Band Registration
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0066')
        self.register_plugin('xep_0071')
        self.register_plugin('xep_0128')
        self.register_plugin('xep_0363')

        # EVENT HANDLERS
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("session_start", self.app)
        self.add_event_handler("message", self.recv_message)
        self.add_event_handler("groupchat_message", self.recv_muc_message)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler("groupchat_presence", self.muc_online)
        # Notifications
        self.add_event_handler("chatstate_active", self.recv_notifications)
        self.add_event_handler("chatstate_composing", self.recv_notifications)
        self.add_event_handler("chatstate_gone", self.recv_notifications)
        self.add_event_handler("chatstate_inactive", self.recv_notifications)
        self.add_event_handler("chatstate_paused", self.recv_notifications)

        self.received = set()
        self.presences_received = asyncio.Event()


    async def session_start(self, event):
        """ Session start. Must send presence to server and get JID's roster. """

        try:
            await self.get_roster()
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')
        self.send_presence()


    async def unregister(self):
        """ Unregister an account. """
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['remove'] = True

        try:
            await resp.send()
            logging.info("Account removed successfully.")
            self.disconnect()
        except IqError as e:
            print("Could not remove account.")
            logging.error(f"Could not remove account: {e}")
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


    def recv_message(self, msg):
        """ Handles incoming messages. """

        if msg['type'] in ('chat', 'normal'):
            print(f"{msg['from'].username}: {msg['body']}")
            # msg.reply("Thanks for sending\n%(body)s" % msg).send() #msg['body']
            
        elif msg['type'] in ('error'):
            print('An error has ocurred.')

        elif msg['type'] in ('headline'):
            print(f"Headline: {msg['body']}")

        elif msg['type'] in ('groupchat'):
            print(f"{msg['from'].username}: {msg['body']}")


    def message(self, recipient, message=None, chat_state='active', mtype='chat'):
        """ Sends message to another user in server. """

        recipient = clean_jid(recipient) # Check for domain
        msg = self.Message()
        msg['chat_state'] = chat_state
        msg['to'] = recipient
        msg['body'] = message
        msg['type'] = mtype 

        msg.send()


    def recv_muc_message(self, msg):
        """ Process incoming message stanzas from any chat room.

            Arguments:
                msg -- The received message stanza. See the documentation
                    for stanza objects and the Message stanza to see
                    how it may be used.
        """

        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            logging.info(f"You've been mentioned by {msg['mucnick']}")


    def wait_for_presences(self, pres):
        """ Track how many roster entries have received presence updates. """

        if pres['type']=='unavailable':
            print(f"{pres['from'].username} is now offline.")

        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()


    def muc_online(self, presence):
        """ Process a presence stanza from a chat room.

            In this case, presences from users that have just come
            online are handled by sending a welcome message that
            includes the user's nickname and role in the room.
        """

        if presence['muc']['nick'] != self.nick:
            print(f"{presence['from'].bare} {presence['muc']['role']} {presence['muc']['nick']} is online!")


    def recv_notifications(self, event):
        if event['chat_state'] == 'active':
            print(f"{event['from'].username} is active.")
        elif event['chat_state'] == 'composing':
            print(f"{event['from'].username} is typing...")
        elif event['chat_state'] == 'gone':
            print(f"{event['from'].username} is gone.")


    def print_roster(self):
        print('Roster for %s' % self.boundjid.username)
        groups = self.client_roster.groups()
        for group in groups:
            print('\n%s' % group)
            print('-' * 72)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print(' %s (%s) [%s]' % (name, jid, sub))
                else:
                    print(' %s [%s]' % (jid, sub))

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    print('   - %s (%s)' % (res, show))
                    if pres['status']:
                        print('       %s' % pres['status'])


    async def app(self, event):
        IN_APP_LOOP = True

        while IN_APP_LOOP:

            print(settings.MAIN_MENU)
            option = int(await ainput("\nSelect an option: "))

            if option==1: # Show roster
                self.print_roster()

            elif option==2: # Add contact
                recipient = str(await ainput("\nJID of new contact: "))
                recipient = clean_jid(recipient)

                self.send_presence_subscription(pto=recipient)

            elif option==3: # Show contact details
                contact = str(await ainput("\nContact's JID: "))

                if contact in self.client_roster:

                    print("Name: ", self.client_roster[contact]['name'] or contact)
                    conns = self.client_roster.presence(contact)
                    for res, pres in conns.items():
                        show = 'available'
                        if pres['show']:
                            show = pres['show']
                        print('   - %s (%s)' % (res, show))
                        if pres['status']:
                            print('       %s' % pres['status'])


                    groups = self.client_roster[contact]['groups']
                    if not groups:
                        print("\nNo shared groups.")
                    else:
                        print("Shared groups: ")
                        for group in groups:
                            print(f"\t{group}")
                
                else:
                    print(f"{contact} is not in your contacts!")

            elif option==4: # Send direct message
                recipient = str(await ainput("JID: "))
                recipient = clean_jid(recipient)

                print(f"\nChatting with {recipient}")
                print("Type 'exit' to exit chat.")

                IN_CHAT = True

                self.message(recipient, chat_state='active')

                while IN_CHAT:
                    self.message(recipient, chat_state='composing')
                    msg = str(await ainput(">> "))
                    if msg != 'exit':
                        self.message(recipient, msg)
                    else:
                        self.message(recipient, chat_state='gone')
                        IN_CHAT = False

            elif option==5: # Change presence
                print(settings.PSHOW_MENU)
                show = str(await ainput("Select showtype: "))
                status = str(await ainput("Status: "))
                nick = str(await ainput("Nickname: "))
                
                self.send_presence(pshow=show, pstatus=status, pnick=nick)

            elif option==6: # Groupchat
                if settings.TESTING and settings.TEST_ROOM:
                    room = settings.TEST_ROOM
                else:
                    room = str(await ainput("Room: "))
                nick = str(await ainput("Nickname: "))

                self.nick = nick

                self.plugin['xep_0045'].join_muc(room, nick)

                print(f"Joined {room}!")
                print("Type 'exit' to exit room.")

                IN_CHAT = True

                while IN_CHAT:
                    msg = str(await ainput(">> "))
                    if msg != 'exit':
                        self.send_message(room, msg, mtype='groupchat')
                    else:
                        print(f"Leaving {room}")
                        self.nick = None
                        self.plugin['xep_0045'].leave_muc(room, nick)
                        IN_CHAT = False
                
            elif option==7: # Send file
                recipient = str(await ainput("Recipient: "))
                filename = str(await ainput("Filename: "))
                domain = str(await ainput("Domain: "))

                try:
                    url = await self['xep_0363'].upload_file(
                        filename, domain=domain, timeout=10
                    )
                except IqTimeout:
                    raise TimeoutError('Could not send message in time')
                logging.info('Upload success!')

                logging.info('Sending file to %s', recipient)
                html = (
                    f'<body xmlns="http://www.w3.org/1999/xhtml">'
                    f'<a href="{url}">{url}</a></body>'
                )
                message = self.make_message(mto=recipient, mbody=url, mhtml=html)
                message['oob']['url'] = url
                message.send()        

            elif option==8: # Logout
                print("Logout")
                IN_APP_LOOP = False
                self.disconnect()
                pass

            elif option==9: # Delete my account
                print("Delete my account")
                await self.unregister()
                pass

            elif option==10: # Exit
                print("Exit")
                print("Goodbye!")
                sys.exit()

            else:
                print("Not a valid option.")


