##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Translation Service Message Export and Import Filters

$Id: filters.py,v 1.2 2003/03/25 23:25:12 bwarsaw Exp $
"""
import time, re
from types import StringTypes

from zope.i18n.interfaces import IMessageExportFilter
from zope.i18n.interfaces import IMessageImportFilter
from zope.app.interfaces.services.translation import ILocalTranslationService


class GettextExportFilter:

    __implements__ =  IMessageExportFilter
    __used_for__ = ILocalTranslationService


    def __init__(self, service):
        self.service = service

    def exportMessages(self, domains, languages):
        'See IMessageExportFilter'

        if isinstance(domains, StringTypes):
            domain = domains
        elif len(domains) == 1:
            domain = domains[0]
        else:
            raise TypeError, \
                  'Only one domain at a time is supported for gettext export.'

        if isinstance(languages, StringTypes):
            language = languages
        elif len(languages) == 1:
            language = languages[0]
        else:
            raise TypeError, \
                'Only one language at a time is supported for gettext export.'

        dt = time.time()
        dt = time.localtime(dt)
        dt = time.strftime('%Y/%m/%d %H:%M', dt)
        output = _file_header %(dt, language.encode('UTF-8'),
                                domain.encode('UTF-8'))
        service = self.service

        for msgid in service.getMessageIdsOfDomain(domain):
            msgstr = service.translate(domain, msgid,
                                       target_language=language)
            msgstr = msgstr.encode('UTF-8')
            msgid = msgid.encode('UTF-8')
            output += _msg_template %(msgid, msgstr)

        return output



class GettextImportFilter:

    __implements__ =  IMessageImportFilter
    __used_for__ = ILocalTranslationService


    def __init__(self, service):
        self.service = service

    def importMessages(self, domains, languages, file):
        'See IMessageImportFilter'

        if isinstance(domains, StringTypes):
            domain = domains
        elif len(domains) == 1:
            domain = domains[0]
        else:
            raise TypeError, \
                  'Only one domain at a time is supported for gettext export.'

        if isinstance(languages, StringTypes):
            language = languages
        elif len(languages) == 1:
            language = languages[0]
        else:
            raise TypeError, \
                'Only one language at a time is supported for gettext export.'

        result = parseGetText(file.readlines())[3]
        headers = parserHeaders(''.join(result[('',)][1]))
        del result[('',)]
        charset = extractCharset(headers['content-type'])
        service = self.service
        for msg in result.items():
            msgid = unicode(''.join(msg[0]), charset)
            msgid = msgid.replace('\\n', '\n')
            msgstr = unicode(''.join(msg[1][1]), charset)
            msgstr = msgstr.replace('\\n', '\n')
            service.addMessage(domain, msgid, msgstr, language)



def extractCharset(header):
    charset = header.split('charset=')[-1]
    return charset.lower()


def parserHeaders(headers_text):
    headers = {}
    for line in headers_text.split('\\n'):
        name = line.split(':')[0]
        value = ''.join(line.split(':')[1:])
        headers[name.lower()] = value

    return headers


def parseGetText(content):
    # The regular expressions
    com = re.compile('^#.*')
    msgid = re.compile(r'^ *msgid *"(.*?[^\\]*)"')
    msgstr = re.compile(r'^ *msgstr *"(.*?[^\\]*)"')
    re_str = re.compile(r'^ *"(.*?[^\\])"')
    blank = re.compile(r'^\s*$')

    trans = {}
    pointer = 0
    state = 0
    COM, MSGID, MSGSTR = [], [], []
    while pointer < len(content):
        line = content[pointer]
        #print 'STATE:', state
        #print 'LINE:', line, content[pointer].strip()
        if state == 0:
            COM, MSGID, MSGSTR = [], [], []
            if com.match(line):
                COM.append(line.strip())
                state = 1
                pointer = pointer + 1
            elif msgid.match(line):
                MSGID.append(msgid.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 0, line %d\n' % (pointer + 1)
        elif state == 1:
            if com.match(line):
                COM.append(line.strip())
                state = 1
                pointer = pointer + 1
            elif msgid.match(line):
                MSGID.append(msgid.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 1, line %d\n' % (pointer + 1)

        elif state == 2:
            if com.match(line):
                COM.append(line.strip())
                state = 2
                pointer = pointer + 1
            elif re_str.match(line):
                MSGID.append(re_str.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif msgstr.match(line):
                MSGSTR.append(msgstr.match(line).group(1))
                state = 3
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 2, line %d\n' % (pointer + 1)

        elif state == 3:
            if com.match(line) or msgid.match(line):
                # print "\nEn", language, "detected", MSGID
                trans[tuple(MSGID)] = (COM, MSGSTR)
                state = 0
            elif re_str.match(line):
                MSGSTR.append(re_str.match(line).group(1))
                state = 3
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 3, line %d\n' % (pointer + 1)

    # the last also goes in
    if tuple(MSGID):
        trans[tuple(MSGID)] = (COM, MSGSTR)

    return COM, MSGID, MSGSTR, trans


_file_header = '''
msgid ""
msgstr ""
"Project-Id-Version: Zope 3\\n"
"PO-Revision-Date: %s\\n"
"Last-Translator: Zope 3 Gettext Export Filter\\n"
"Zope-Language: %s\\n"
"Zope-Domain: %s\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
'''

_msg_template = '''
msgid "%s"
msgstr "%s"
'''
