##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""SMTP mail objects

$Id: MailHost.py,v 1.65 2002/01/15 04:05:12 jens Exp $"""
__version__ = "$Revision: 1.65 $"[11:-2]

from Globals import Persistent, DTMLFile, MessageDialog, InitializeClass
from smtplib import SMTP
from AccessControl.Role import RoleManager
from operator import truth
import Acquisition, sys, string, types, mimetools
import OFS.SimpleItem, re, quopri, rfc822
from cStringIO import StringIO
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, \
                                      use_mailhost_services

smtpError = "SMTP Error"
MailHostError = "MailHost Error"

manage_addMailHostForm=DTMLFile('dtml/addMailHost_form', globals())
def manage_addMailHost(self, id, title='', smtp_host=None,
                       localhost='localhost', smtp_port=25,
                       timeout=1.0, REQUEST=None):
    ' add a MailHost into the system '

    id=str(id)
    title=str(title)
    if smtp_host is not None:
        smtp_host=str(smtp_host)
    if type(smtp_port) is not type(1):
        smtp_port=string.atoi(smtp_port)

    i=MailHost()            #create new mail host
    i.id=id                 #give it id
    i.title=title           #title
    i._init(smtp_host=smtp_host, smtp_port=smtp_port)

    self=self.this()
    self._setObject(id,i)   #register it
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

add = manage_addMailHost

class MailBase(Acquisition.Implicit, OFS.SimpleItem.Item, RoleManager):
    'a mailhost...?'
    meta_type='Mail Host'
    manage=manage_main=DTMLFile('dtml/manageMailHost', globals())
    manage_main._setName('manage_main')
    index_html=None
    security = ClassSecurityInfo()

    timeout=1.0

    manage_options=(
        (
        {'icon':'', 'label':'Edit',
         'action':'manage_main', 'target':'manage_main',
         'help':('MailHost','Mail-Host_Edit.stx')},
        )
        +RoleManager.manage_options
        +OFS.SimpleItem.Item.manage_options
        )


    def __init__(self):
        'nothing yet'
        pass

    def _init(self, smtp_host, smtp_port):
        self.smtp_host=smtp_host
        self.smtp_port=smtp_port

    security.declareProtected( 'Change configuration', 'manage_makeChanges' )
    def manage_makeChanges(self,title,smtp_host,smtp_port, REQUEST=None):
        'make the changes'

        title=str(title)
        smtp_host=str(smtp_host)
        if type(smtp_port) is not type(1):
            smtp_port=string.atoi(smtp_port)

        self.title=title
        self.smtp_host=smtp_host
        self.smtp_port=smtp_port
        if REQUEST: return MessageDialog(
            title  ='Changed %s' % self.__name__,
            message='%s has been updated' % self.id,
            action =REQUEST['URL2']+'/manage_main',
            target ='manage_main')
    
    security.declareProtected( use_mailhost_services, 'sendTemplate' )
    def sendTemplate(trueself, self, messageTemplate, 
                     statusTemplate=None, mto=None, mfrom=None,
                     encode=None, REQUEST=None):
        'render a mail template, then send it...'
        mtemplate = getattr(self, messageTemplate)
        messageText = mtemplate(self, trueself.REQUEST)
        messageText=_encode(messageText, encode)
        headers = extractheaders(messageText)
        if mto: headers['to'] = mto
        if mfrom: headers['from'] = mfrom
        for requiredHeader in ('to', 'from'):
            if not headers.has_key(requiredHeader):
                raise MailHostError,"Message missing SMTP Header '%s'"\
                      % requiredHeader
        mailserver = SMTP(trueself.smtp_host, trueself.smtp_port)
        mailserver.sendmail(headers['from'], headers['to'], messageText)

        if not statusTemplate: return "SEND OK"

        try:
            stemplate=getattr(self, statusTemplate)
            return stemplate(self, trueself.REQUEST)
        except:
            return "SEND OK"

    security.declareProtected( use_mailhost_services, 'send' )
    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None):
        headers = extractheaders(messageText)

        messageText = messageText.lstrip()

        if not headers['subject'] and len(headers)==0:
            messageText="subject: %s\n\n%s" % (subject or '[No Subject]',
                                             messageText)

        elif not headers['subject']: 
            messageText="subject: %s\n%s" % (subject or '[No Subject]',
                                             messageText)


        if mto:
            if type(mto) is type('s'):
                mto=map(string.strip, string.split(mto,','))
            headers['to'] = filter(None, mto)
        if mfrom:
            headers['from'] = mfrom
            
        for requiredHeader in ('to', 'from'):
            if not headers.has_key(requiredHeader):
                raise MailHostError,"Message missing SMTP Header '%s'"\
                % requiredHeader
        messageText=_encode(messageText, encode)
        smtpserver = SMTP(self.smtp_host, self.smtp_port)
        smtpserver.sendmail(headers['from'],headers['to'], messageText)

    security.declareProtected( use_mailhost_services, 'scheduledSend' )
    def scheduledSend(self, messageText, mto=None, mfrom=None, subject=None,
                      encode=None):
        """Looks like the same function as send() - scheduledSend() is nowhere 
        used in Zope. No idea if it is still needed/used (ajung)
        """

        headers = extractheaders(messageText)

        if not headers['subject']:
            messageText="subject: %s\n%s" % (subject or '[No Subject]',
                                             messageText)
        if mto:
            if type(mto) is type('s'):
                mto=map(string.strip, string.split(mto,','))
            headers['to'] = filter(truth, mto)
        if mfrom:
            headers['from'] = mfrom

        for requiredHeader in ('to', 'from'):
            if not headers.has_key(requiredHeader):
                raise MailHostError,"Message missing SMTP Header '%s'"\
                % requiredHeader
        messageText=_encode(messageText, encode)
        smtpserver = SMTP(self.smtp_host, self.smtp_port)
        smtpserver.sendmail(headers['from'], headers['to'], messageText)

    security.declareProtected( use_mailhost_services, 'simple_send' )
    def simple_send(self, mto, mfrom, subject, body):
        body="from: %s\nto: %s\nsubject: %s\n\n%s" % (
            mfrom, mto, subject, body)
        mailserver = SMTP(self.smtp_host, self.smtp_port)
        mailserver.sendmail(mfrom, mto, body)

        
InitializeClass( MailBase )

class MailHost(Persistent, MailBase):
    "persistent version"

def _encode(body, encode=None):
    if encode is None:
        return body
    mfile=StringIO(body)
    mo=mimetools.Message(mfile)
    if mo.getencoding() != '7bit': 
        raise MailHostError, 'Message already encoded'
    newmfile=StringIO()
    newmfile.write(string.joinfields(mo.headers, ''))
    newmfile.write('Content-Transfer-Encoding: %s\n' % encode)
    if not mo.has_key('Mime-Version'):
        newmfile.write('Mime-Version: 1.0\n')
    newmfile.write('\n')
    mimetools.encode(mfile, newmfile, encode)
    return newmfile.getvalue()


def extractheaders(message):
    # return headers of message
    mfile=StringIO(string.strip(message))
    mo=rfc822.Message(mfile)

    hd={}
    hd['to']=[]
    for header in (mo.getaddrlist('to'),
                   mo.getaddrlist('cc'),
                   mo.getaddrlist('bcc')):
        if not header: continue
        for name, addr in header:
            hd['to'].append(addr)
    
    hd['from']=mo.getaddr('from')[1]
    hd['subject']=mo.getheader('subject') or ''
    return hd
