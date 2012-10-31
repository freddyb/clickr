#!/usr/bin/env python
#encoding: utf-8

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

# You can run this module directly with:
#    twistd -ny emailserver.tac

"""
A toy email server.
"""

from zope.interface import implements

from twisted.internet import defer
from twisted.mail import smtp

from twisted.cred.portal import IRealm
from twisted.cred.portal import Portal

from twisted.internet.threads import deferToThread

from scanner import MailHandler

class ClickrMessageDelivery:
    # wenn ich ESMTP subclasse, kann ich eigene handler schreibn
    # für befehle wie DATA, usw.
    implements(smtp.IMessageDelivery)
    
    def receivedHeader(self, helo, origin, recipients):
        try:
            return "Received: from %s (%s); %s" % (helo[1], origin, smtp.rfc822date())
        except KeyError:
            return "Received: from %s (%s); %s" % (helo[0], origin, smtp.rfc822date()) # never tried ;P

    
    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin

    
    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        #if user.dest.local == "console":
        return ClickrMessage # lambda: ClickrMessage()
        
        raise smtp.SMTPBadRcpt(user)



class ClickrMessage:
    implements(smtp.IMessage)
    
    def __init__(self):
        self.lines = []

    
    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        # we could use an email.FeedParser if we wanted streamlined-
        # parsing, i.e. checking the first few bytes and discarding
        # after N amount of URLs. would save us cpu time and memory
        # but not bandwidth as we have to receive the full email
        # content and answer with a decent "sure, that's *SO* gonna
        # be delivered" (and then delete it ;D)
        deferToThread(MailHandler, "\n".join(self.lines))
        self.lines = None
        return defer.succeed(None)

    
    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None


class SMTPFactory(smtp.SMTPFactory):
    protocol = smtp.ESMTP

    def __init__(self, *a, **kw):
        smtp.SMTPFactory.__init__(self, *a, **kw)
        self.delivery = ClickrMessageDelivery()
    

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.delivery = self.delivery
        #p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p



class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if smtp.IMessageDelivery in interfaces:
            return smtp.IMessageDelivery, ClickrMessageDelivery(), lambda: None
        raise NotImplementedError()



def main():
    from twisted.application import internet
    from twisted.application import service    
    
    portal = Portal(SimpleRealm())
        
    a = service.Application("Clickr SMTP Server")
    internet.TCPServer(2500, SMTPFactory(portal)).setServiceParent(a)
    
    return a

application = main()
