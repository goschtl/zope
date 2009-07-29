
import twisted.conch.ssh.channel
import twisted.conch.ssh.connection
import twisted.conch.ssh.keys
import twisted.conch.ssh.transport
import twisted.conch.ssh.userauth
import twisted.internet.defer
import twisted.internet.protocol
import twisted.internet.reactor

class Transport(twisted.conch.ssh.transport.SSHClientTransport):

    def verifyHostKey(self, pubKey, fingerprint):
        print 'host key fingerprint: %s' % fingerprint
        return twisted.internet.defer.succeed(1) 

    def connectionSecure(self):
        self.requestService(UserAuth('user', Connection()))

class UserAuth(twisted.conch.ssh.userauth.SSHUserAuthClient):

    def getPassword(self, prompt = None):
        return # this says we won't do password authentication

    def getPublicKey(self):
        return twisted.conch.ssh.keys.Key.fromFile('ukey.pub').blob()

    def getPrivateKey(self):
        return twisted.internet.defer.succeed(
            twisted.conch.ssh.keys.Key.fromFile('ukey').keyObject)

class Connection(twisted.conch.ssh.connection.SSHConnection):

    def serviceStarted(self):
        self.openChannel(Channel(conn = self))

# Channels are twisted.internet.interfaces.ITransports
class Channel(twisted.conch.ssh.channel.SSHChannel):

    name = 'echo'

    def channelOpen(self, data):
        self.catData = ''
        self.write('This data will be echoed back to us by "cat."\r\n')
        self.conn.sendEOF(self)
        self.loseConnection()

    def dataReceived(self, data):
        self.catData += data

    def closed(self):
        print 'We got this from "cat":', self.catData
        twisted.internet.reactor.stop()

def main():
    factory = twisted.internet.protocol.ClientFactory()
    factory.protocol = Transport
    twisted.internet.reactor.connectTCP('localhost', 5022, factory)
    twisted.internet.reactor.run()

if __name__ == "__main__":
    main()

