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

$Id: metaconfigure.py,v 1.2 2002/12/25 14:12:53 jim Exp $
"""

import os
from zope.configuration.action import Action
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.globaltranslationservice import translationService

def registerTranslations(_context, directory):
    """ """
    actions = []

    path = _context.path(directory)
    path = os.path.normpath(path)

    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if os.path.isdir(lc_messages_path):
            for domain_file in os.listdir(lc_messages_path):
                if domain_file.endswith('.mo'):
                    domain_path = os.path.join(lc_messages_path, domain_file)
                    domain = domain_file[:-3]
                    catalog = GettextMessageCatalog(language, domain,
                                                    domain_path)

                    actions.append(Action(
                        discriminator = catalog.getIdentifier(),
                        callable = translationService.addCatalog,
                        args = (catalog,) ))
    return actions


def defaultLanguages(_context, languages):
    langs = [L.strip() for L in languages.split()]
    return [Action(discriminator = ('gts', languages),
                   callable = translationService.setLanguageFallbacks,
                   args = (langs,))]
