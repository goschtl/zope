##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""SMTP service.

$Id: SmtpService.py
"""

from Persistence import Persistent
from smtplib import SMTP
from operator import truth
import sys, string, types, mimetools
import re, quopri, rfc822
from cStringIO import StringIO
from ISMTPService import ISMTPService

import Exception


        
class SmtpService(Persistent):
    """
    """
    __implements__ = ISMTPService

    def __init__(self, smtphost='localhost', smtpport= 25):
        self.smtphost = smtphost
        self.smtpport = int(smtpport)
        

    
    def sendMessage(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None):
        headers = extractheaders(messageText)

        if not headers['subject']:
            messageText="subject: %s\n\n%s" % (subject or '[No Subject]',
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
        self.__send(messageText, encode, headers['to'], headers['from'])    

    def sendBody(self, mto, mfrom, subject, body, encode=None):
        
        body="from: %s\nto: %s\nsubject: %s\n\n%s" % (
            mfrom, mto, subject, body)
        self.__send(body, encode, mto, mfrom)


    def __send(self, messageText, encode, mto, mfrom):
        if encode:
            messageText=_encode(messageText, encode)
            
        smtpserver = SMTP(self.smtphost, int(self.smtpport))
        smtpserver.sendmail(mfrom, mto, messageText)


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
     
 