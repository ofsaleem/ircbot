#!/usr/bin/env python

import time
from re import findall

from circuits import Component
from circuits.net.events import connect
from circuits.net.sockets import TCPClient
from circuits.protocols.irc import ERR_NICKNAMEINUSE
from circuits.protocols.irc import RPL_ENDOFMOTD, ERR_NOMOTD
from circuits.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN

from requests import get
from lxml.html import fromstring


class Bot(Component):

    def init(self, host, port=6667):
        self.host = host
        self.port = port

        TCPClient().register(self)
        IRC().register(self)

    def ready(self, component):
        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        self.fire(USER("VTqq", host, host, "Link Parser Bot"))
        self.fire(NICK("VTqq"))

    def numeric(self, source, numeric, *args):
        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("%s_" % args))
        if numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.fire(PRIVMSG("NICKSERV", "identify iamvtqqbot"))
            time.sleep(5)
            self.fire(JOIN("#vtqq"))
            self.fire(JOIN("#vtqq"))
            self.fire(JOIN("#vtqq"))

    def privmsg(self, source, target, message):
        if target[0] == "#":
            urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message)  # noqa
            if urls:
                url = urls[0]
                response = get(url)
                if response.status_code == 200:
                    doc = fromstring(response.text)
                    title = doc.cssselect("title")
                    if title:
                        title = title[0].text.strip()
                        self.fire(
                            PRIVMSG(
                                target,
                                "Link Title: {0:s}".format(
                                    title
                                )
                            )
                        )
        else:
            self.fire(PRIVMSG(source[0], message))


bot = Bot("irc.rizon.net")

bot.run()
