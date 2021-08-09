# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

import slixmpp
from slixmpp.exceptions import IqError, IqTimeout


class RegisterBot(slixmpp.ClientXMPP):
    """ A basic bot that will attempt to register an account with an XMPP server. """

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration


        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)

    async def start(self, event):
        """ Process the session_start event. """
        self.send_presence()
        await self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()

    async def register(self, iq):
        """ Fill out and submit a registration form. """

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            logging.info("Account created for %s!" % self.boundjid)
            
        except IqError as e:
            if e.iq['error']['code']=='409':
                logging.error(f"An account already exists for user: {e.iq['register']['username']}.")
            else:
                logging.error(f"Could not register account: {e.iq['error']['text']}")
            self.disconnect()

        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()

