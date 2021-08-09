
import asyncio
import logging
from re import L, M
import settings
import sys

import slixmpp
from slixmpp.exceptions import IqError, IqTimeout, XMPPError
from aioconsole import ainput


class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        #Plugins

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        #Registration
        self.register_plugin('xep_0077')
        #MUC
        self.register_plugin('xep_0045') # Multi-User Chat

        # Event handlers
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("session_start", self.app)
        self.add_event_handler("message", self.recv_message)
        self.add_event_handler("groupchat_message", self.recv_muc_message)


        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

    async def session_start(self, event):
        """ Session start. Must send presence to server and get JID's roster. """

        self.send_presence()
        try:
            await self.get_roster() # Denfesive programming could be added.

            print(self.client_roster)
        except IqError as e:
            logging.error(f"Could not get roster: {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            logging.error(f"Timeout while getting roster.")
            self.disconnect()

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
            print(f"Message received from {msg['from'].username}: {msg['body']}")
            # msg.reply("Thanks for sending\n%(body)s" % msg).send() #msg['body']
            
        elif msg['type'] in ('error'):
            print('An error has ocurred.')

        elif msg['type'] in ('headline'):
            print('Headline message received.')

        elif msg['type'] in ('groupchat'):
            print('Groupchat message received.')

    def message(self, recipient, message, mtype='chat'):
        """ Sends message to another user in server. """

        self.send_message(recipient, message, mtype)

    def recv_muc_message(self, msg):
        """ Process incoming message stanzas from any chat room. Be aware
            that if you also have any handlers for the 'message' event,
            message stanzas may be processed by both handlers, so check
            the 'type' attribute when using a 'message' event handler.

            Whenever the bot's nickname is mentioned, respond to
            the message.

            This handler will reply to messages that mention
            the bot's nickname.

            Arguments:
                msg -- The received message stanza. See the documentation
                    for stanza objects and the Message stanza to see
                    how it may be used.
        """

        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            self.send_message(
                mto=msg['from'].bare,
                mbody="I heard that, %s." % msg['mucnick'],
                mtype='groupchat'
            )

    def muc_online(self, presence):
        """ Process a presence stanza from a chat room. In this case,
            presences from users that have just come online are
            handled by sending a welcome message that includes
            the user's nickname and role in the room.

            Arguments:
                presence -- The received presence stanza. See the
                            documentation for the Presence stanza
                            to see how else it may be used.
        """

        if presence['muc']['nick'] != self.nick:
            self.send_message(
                mto=presence['from'].bare,
                mbody=f"Hello, %{presence['muc']['role']} %{presence['muc']['nick']}",
                mtype='groupchat'
            )

    async def app(self, event):
        IN_APP_LOOP = True

        while IN_APP_LOOP:
            print(settings.MAIN_MENU)
            option = int(await ainput("\nSelect an option: "))

            if option==1: # Add contact
                print("Ingrese el contacto que desea agregar:")
                pass

            elif option==2: # Show contact details
                print("Show contact details")
                pass

            elif option==3: # Send direct message
                recipient = str(await ainput("Send message to: "))
                msg = str(await ainput(">>: "))

                self.message(recipient, msg)
                pass

            elif option==4: # Change presence
                print("Change presence")
                pass

            elif option==5: # Groupchat
                print("Groupchat")
                pass

            elif option==6: # Logout
                print("Logout")
                IN_APP_LOOP = False
                self.disconnect()
                pass

            elif option==7: # Delete my account
                print("Delete my account")
                await self.unregister()
                pass

            elif option==8: # Exit
                print("Exit")
                print("Goodbye!")
                sys.exit()

            else:
                print("Enter a valid option.")


