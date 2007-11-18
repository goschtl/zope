##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Generate an Introduction HTML page for the KGS.

Usage: %s output-intro-path

* ``output-intro-path``

  The path of the file under which the generated intro file is stored.
"""
import os
import zope.pagetemplate.pagetemplatefile

FEATURES = [
    ('controlled-packages-%(version)s.cfg', u'Controlled Packages'),
    ('buildout-%(version)s.cfg',            u'Buildout Configuration'),
    ('versions-%(version)s.cfg',            u'Versions'),
    ('links-%(version)s.html',              u'Package Links'),
    ('index.html',                          u'Index'),
    ('minimal',                             u'Minimal Index'),
    ]

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'intro.pt')

class IntroPage(zope.pagetemplate.pagetemplatefile.PageTemplateFile):

    def __init__(self, kgsDir):
        super(IntroPage, self).__init__(TEMPLATE_PATH)
        self.kgsDir = kgsDir

    def update(self):
        kgsFileNames = os.listdir(self.kgsDir)
        vnums = [fn[20:-4] for fn in kgsFileNames
                 if fn.startswith('controlled-packages-')]
        vnums.sort()
        self.versions = []
        for vnum in vnums:
            features = []
            for (templ, title) in FEATURES:
                featureFileName = templ %{'version': vnum}
                if featureFileName in kgsFileNames:
                    features.append({'url': featureFileName, 'title': title})
            self.versions.append({'name': vnum, 'features': features})


    def pt_getContext(self, args=(), options=None, **ignore):
        rval = {'args': args,
                'nothing': None,
                'options': options,
                'self': self
                }
        rval.update(self.pt_getEngine().getBaseNames())
        return rval


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 0:
        print __file__.__doc__
        sys.exit(1)

    outputPath = args[0]

    page = IntroPage(os.path.dirname(outputPath))
    page.update()
    open(outputPath, 'w').write(page())
