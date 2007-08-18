##########################################################################
# A transaction-aware Mailhost implementation based on zope.sendmail
#
# (C) Zope Corporation and Contributors
# Written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import os
import logging
from cStringIO import StringIO

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import use_mailhost_services, view_management_screens
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.sendmail.mailer import SMTPMailer
from zope.sendmail.delivery import DirectMailDelivery

LOG = logging.getLogger('TransactionalMailHost')


class MailHost(SimpleItem, PropertyManager):
    """ A transaction-aware MailHost implementation """

    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options
    _properties = (
        {'id' : 'smtp_host', 'type' : 'string', 'mode' : 'rw', },
        {'id' : 'smtp_port', 'type' : 'int', 'mode' : 'rw'}, 
        {'id' : 'smtp_username', 'type' : 'string', 'mode' : 'rw'}, 
        {'id' : 'smtp_password', 'type' : 'string', 'mode' : 'rw'}, 
    )

    id = 'MailHost'
    meta_type = 'TransactionalMailHost'
    smtp_host = 'localhost'
    smtp_port = 25
    smtp_username = ''
    smtp_password = ''

    security = ClassSecurityInfo()

    def __init__(self, id, title='', smtp_host='localhost', smtp_port=25, 
                 smtp_username='', smtp_password=''):
        self.id = id
        self.title = title
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password 


    def _getMailer(self):
        """ Create a new SMTPMailer instance """

        if not hasattr(self, '_v_mailhost'):
            self._v_mailer = SMTPMailer(self.smtp_host,
                                        self.smtp_port,
                                        self.smtp_username or None,
                                        self.smtp_password or None)

        return self._v_mailer


    security.declareProtected(use_mailhost_services, 'send')
    def send(self, message, fromaddr, toaddrs, subject=None, encode=None):
        """ Send out a mail.
            'subject' and 'encode' are unused (and kept right now
            for backward compatibility.
        """

        delivery = DirectMailDelivery(self._getMailer())
        delivery.send(fromaddr, toaddrs, message)
        LOG.debug('Sending mail from %s to %s succeeded' % (fromaddr, toaddrs))


    security.declareProtected(view_management_screens, 'manage_editProperties')
    def manage_editProperties(self, REQUEST):
        """ Invalidate _v_mailer """

        if hasattr(self, '_v_mailer'):
            del self._v_mailer

        return super(MailHost, self).manage_editProperties(REQUEST)


InitializeClass(MailHost)



def manage_addMailHost(self, id='MailHost', title='', smtp_host='localhost', smtp_port=25, 
                       smtp_username='', smtp_password='', RESPONSE=None):
    """ create a new MailHost instance """
    
    mh = MailHost(id, title, smtp_host, smtp_port, smtp_username, smtp_password)
    self._setObject(mh.getId(), mh.__of__(self))
    if RESPONSE:
        return RESPONSE.redirect(self._getOb(id).absolute_url() + '/manage_workspace')
    else:
        return mh

manage_addMailHostForm = PageTemplateFile('pt/addMailHostForm', 
                                           globals(), 
                                           __name__='addMailhostForm')
