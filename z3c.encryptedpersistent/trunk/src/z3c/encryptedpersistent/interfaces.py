##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

class IEncryption(zope.interface.Interface):
    """Utility providing encryption mechanism"""

    def encrypt(key, data):
        """Returns the encrypted data"""

    def decrypt(key, data):
        """Returns the decrypted data"""

class IEncryptedPersistent(zope.interface.Interface):
    """A persistent object that encrypts its state for storage."""

    __key__ = zope.schema.Field(
        title=u'Encryption Key',
        description=(u'Encryption key/state/hint that can be used to aid '
                     u'the encruption and decryption process. This attribute '
                     u'can be any data structure that is necessary to '
                     u'complete the task.'),
        default=None,
        required=False)
