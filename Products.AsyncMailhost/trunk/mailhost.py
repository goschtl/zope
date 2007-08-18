##########################################################################
# A transaction-aware Mailhost implementation based on zope.sendmail
#
# (C) Zope Corporation and Contributors
# Written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import os
import logging
import random
import time

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import zope.sendmail


LOG = logging.getLogger('AsyncMailHost')



class MailHost(SimpleItem, PropertyManager):
    """ A transaction-aware MailHost implementation """

    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options
    _properties = (
        {'id' : 'smtp_host', 'type' : 'string', 'mode' : 'rw', },
        {'id' : 'smtp_port', 'type' : 'int', 'mode' : 'rw'}, 
    )

    id = 'MailHost'
    meta_type = 'AsyncMailHost'
    smtp_host = 'localhost'
    smtp_port = 25

    security = ClassSecurityInfo()

    def __init__(self, id, title='', smtp_host='localhost', smtp_port=25):
        self.id = id
        self.title = title
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port


InitializeClass(MailHost)



def manage_addMailHost(self, id='MailHost', title='', smtp_host='localhost', smtp_port=25, RESPONSE=None):
    """ create a new MailHost instance """
    
    mh = MailHost(id, title, smtp_host, smtp_port)
    self._setObject(mh.getId(), mh.__of__(self))
    if RESPONSE:
        return RESPONSE.redirect(self._getOb(id).absolute_url() + '/manage_workspace')
    else:
        return mh

manage_addMailHostForm = PageTemplateFile('pt/addMailHostForm', 
                                           globals(), 
                                           __name__='addMailhostForm')
