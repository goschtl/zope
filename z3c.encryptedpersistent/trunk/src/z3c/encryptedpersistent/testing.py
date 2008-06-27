##############################################################################
#
# Copyright (c) 2008 by JSA Technologies, Inc
#
##############################################################################
"""
$Id$
"""
import zope.interface

import interfaces


class DemoEncrypter(object):
    zope.interface.implements(interfaces.IEncryption)

    _EncryptionString = "ENCRYPTED_"

    def encrypt(self, data):
        return self._EncryptionString + data

    def decrypt(self, data):
        return data.lstrip(self._EncryptionString)
