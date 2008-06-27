##############################################################################
#
# Copyright (c) 2008 by JSA Technologies, Inc
#
##############################################################################
"""
$Id$
"""
import zope.interface
from z3c.encryptedpersistent import interfaces

class DemoEncrypter(object):
    zope.interface.implements(interfaces.IEncryption)

    _EncryptionString = "ENCRYPTED_"

    def encrypt(self, key, data):
        """See interfaces.IEncryption"""
        return self._EncryptionString + str(key) + data

    def decrypt(self, key, data):
        """See interfaces.IEncryption"""
        return data.lstrip(self._EncryptionString + str(key))
