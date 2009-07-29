#!/usr/bin/python
import sys
import twisted.cred.portal
import twisted.conch.avatar
import twisted.conch.checkers
import twisted.conch.ssh.channel
import twisted.conch.ssh.factory
import twisted.conch.ssh.userauth
import twisted.conch.ssh.connection
import twisted.conch.ssh.keys
import twisted.internet.reactor
import twisted.python.log
import zope.interface

twisted.python.log.startLogging(sys.stderr)

"""Example of running another protocol over an SSH channel.
log in with username "user" and password "password".
"""

# Channels are twisted.internet.interfaces.ITransports.
# We would normally associate a protocol.
class Channel(twisted.conch.ssh.channel.SSHChannel):

    name = 'echo'

    def dataReceived(self, data):
        if data == '\r':
            data = '\r\n'
        elif data == '\x03': #^C
            self.loseConnection()
            return
        self.write(data.upper())

class ExampleAvatar(twisted.conch.avatar.ConchUser):

    def __init__(self, username):
        twisted.conch.avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update(
            {'echo': Channel}
            )

class ExampleRealm:
    zope.interface.implements(twisted.cred.portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], ExampleAvatar(avatarId), lambda: None

user_pubkey = twisted.conch.ssh.keys.Key.fromFile('ukey.pub')

class InMemoryPublicKeyChecker(twisted.conch.checkers.SSHPublicKeyDatabase):

    def checkKey(self, credentials):
        return (credentials.username == 'user' and
                user_pubkey.blob() == credentials.blob)

class ExampleFactory(twisted.conch.ssh.factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile('skey.pub')
    }
    privateKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile('skey')
    }
    services = {
        'ssh-userauth': twisted.conch.ssh.userauth.SSHUserAuthServer,
        'ssh-connection': twisted.conch.ssh.connection.SSHConnection
    }

portal = twisted.cred.portal.Portal(ExampleRealm())
portal.registerChecker(InMemoryPublicKeyChecker())
ExampleFactory.portal = portal

if __name__ == '__main__':
    twisted.internet.reactor.listenTCP(5022, ExampleFactory())
    twisted.internet.reactor.run()
