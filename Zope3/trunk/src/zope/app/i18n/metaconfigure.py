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
"""
This module handles the :startup directives.

$Id: metaconfigure.py,v 1.3 2003/08/03 20:58:38 philikon Exp $
"""

import os
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.globaltranslationservice import translationService

def registerTranslations(_context, directory):
    path = os.path.normpath(directory)

    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if os.path.isdir(lc_messages_path):
            for domain_file in os.listdir(lc_messages_path):
                if domain_file.endswith('.mo'):
                    domain_path = os.path.join(lc_messages_path, domain_file)
                    domain = domain_file[:-3]
                    catalog = GettextMessageCatalog(language, domain,
                                                    domain_path)

                    _context.action(
                        discriminator = catalog.getIdentifier(),
                        callable = translationService.addCatalog,
                        args = (catalog,)
                        )

def defaultLanguages(_context, languages):
    return _context.action(
        discriminator = ('gts', tuple(languages)),
        callable = translationService.setLanguageFallbacks,
        args = (languages,)
        )
