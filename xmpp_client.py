
import asyncio
import logging
from re import L
import settings


import slixmpp
from slixmpp.exceptions import IqError, IqTimeout


class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.rcv_message)
        self.add_event_handler("register", self.register)
        self.add_event_handler("groupchat_message", self.rcv_muc_message)

        #Plugins

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        # Registration
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data 
        self.register_plugin('xep_0077') # In-band Registration
        #MUC
        self.register_plugin('xep_0045') # Multi-User Chat

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')


    async def session_start(self, event):
        """ Session start. Must send presence to server and get JID's roster. """

        self.send_presence()
        try:
            await self.get_roster() # Denfesive programming could be added.
        except IqError as e:
            logging.error(f"Could not get roster: {e.iq['error']['text']}")
            self.disconnect()


    async def register(self, iq):
        """ Fill out and submit a registration form. """

        print("ATTEMPT - REGISTER")

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            logging.info("Account created for %s!" % self.boundjid)

        except IqError as e:
            logging.error(f"Could not register account: {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


    async def unregister(self, iq):
        """ Unregister an account. """

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['remove'] = ''

        print(resp)

        try:
            await resp.send()
        except IqError as e:
            print("Could not remove account.")
            logging.error(f"Could not remove account: {e}")
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


    def rcv_message(self, msg):
        """ Handles incoming messages. """

        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send() #msg['body']
            
        elif msg['type'] in ('error'):
            print('An error has ocurred.')

        elif msg['type'] in ('headline'):
            print('Headline message received.')

        elif msg['type'] in ('groupchat'):
            print('Groupchat message received.')


    def send_message(self, recipient, message, mtype='chat'):
        """ Sends message to another user in server. """

        self.send_message(recipient, message, mtype)


    def rcv_muc_message(self, msg):
        """ Process incoming message stanzas from any chat room. Be aware
            that if you also have any handlers for the 'message' event,
            message stanzas may be processed by both handlers, so check
            the 'type' attribute when using a 'message' event handler.

            Whenever the bot's nickname is mentioned, respond to
            the message.

            IMPORTANT: Always check that a message is not from yourself,
                    otherwise you will create an infinite loop responding
                    to your own messages.

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



