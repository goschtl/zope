=====================
Key Management Server
=====================

This package provides a NIST SP 800-57 compliant key management server.

  >>> from z3c.keyserver import server

In order to ensure the highest level of compliance, the key management server
and server storing the data cannot be the same machine. Next, the key used to
en- and decrypt the data cannot be stored in plain format, but must also be
encrypted for storage using a key of equal and better strength.

The workflow to create a new encryption key.

1. Create the key encryption key (private and public).

2. Create the encryption key (private and public).

3. Use the private key encryption key to encrypt both, the private and public,
   encryption key.

4. Discard the private key encryption key.

5. Store the encrypted private and public encryption key on the server.

6. Return the public key encryption key.

So let's create a key management server:

  >>> keys = server.KeyServer()
  >>> keys
  <KeyServer (0)>

  # Later show attributes

 and generate a key:

  >>> key = keys.generate()
  >>> key

You can now use this key encryption key to extract the encryption keys:

  >>> keys.get(key)

You can also ask the key server to encrypt a string directly. This
functionality is provided by the ``IEnryption`` interface:

  >>> from zope.interface import verify
  >>> from z3c.keyserver import interfaces
  >>> verify.verifyObject(interfaces.IEncryption, keys)
  True

Let's now encrypt some data:

  >>> encrypted = keys.encrypt(key, 'Stephan Richter')
  >>> encrypted

We can also decrypt the data.

  >>> keys.decrypt(key, encrypted)
  'Stephan Richter'


And that's pretty much all there is to it. Most of the complicated
crypto-related work happens under the hood, transparent to the user.


The Key Client
--------------

In order to access the key server remotely, we define a simple XML-RPC API to
communicate the keys. We do not make the server responsible for doing the
actual encryption and decryption, so that the key server does not become a
resource bottle neck. A simple component is wrapped around the XML-RPC call:

  >>> from z3c.keyserver import cient
  >>> remoteKeys = client.KeyClient('http://localhost/keys')
  >>> remoteKeys
  <KeyClient 'http://localhost/keys'>

In order to make this work in this test we'll setup a fake connection:

  >>> from z3c.keyserver import testing
  >>> testing.setUpRPC(remoteKeys, keys)

As with the server, the client implements the ``IEncryption`` interfaces:

  >>> verify.verifyObject(interfaces.IEncryption, remoteKeys)
  True

So en- and decryption is very easy to do:

  >>> encrypted = remoteKeys.encrypt(key, 'Stephan Richter')
  >>> encrypted

  >>> remoteKeys.decrypt(key, encrypted)
  'Stephan Richter'

Of course, the client does not fetch the keys for every call. Instead, they
are cached on the client locally:

  >>> key in remoteKeys._cache
  True

A timeout (in seconds) controlls when a key must be refetched:

  >>> remoteKeys.timeout
  3600

Let's now force a reload by setting the timeout to zero:

  >>> remoteKeys.timeout = 0

  >>> firstTime = remoteKeys._cache[key][0]
  remoteKeys.decrypt(key, encrypted)
  >>> secondTime = remoteKeys._cache[key][0]

  >>> firstTime < secondTime
  True

The client can of course also ask the key server to generate a key:

  >>> key2 = remoteKeys.generate()
  >>> key2

The key should be immediately available on the server:

  >>> key2 in keys
  True
