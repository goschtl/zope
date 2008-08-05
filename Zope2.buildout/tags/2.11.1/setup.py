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
"""Setup for the Acquisition egg package
"""
import os
from setuptools import setup, find_packages, Extension

EXTENSIONCLASS_INCLUDEDIRS = ['include', 'lib/python']

setup(name='Zope2',
      version = '2.11.1',
      url='http://www.zope.org',
      license='ZPL 2.1',
      description='Zope2 application server / web framework',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description='',
      
      packages=find_packages('lib/python'),
      package_dir={'': 'lib/python'},

      data_files=[
        ('skel', ['skel/README.txt']),
        ('skel/bin', ['skel/bin/runzope.bat.in',
                      'skel/bin/runzope.in',
                      'skel/bin/zopectl.bat.in',
                      'skel/bin/zopectl.in',
                      'skel/bin/zopeservice.py.in',
                     ]),
        ('skel/etc', ['skel/etc/site.zcml',
                      'skel/etc/zope.conf.in',
                     ]),
        ('skel/etc/package-includes', []),
        ('skel/Extensions', ['skel/Extensions/README.txt']),
        ('skel/import', ['skel/import/Examples.zexp',
                         'skel/import/README.txt',
                         'skel/import/ZopeTutorialExamples.zexp',
                        ]),
        ('skel/lib/python', ['skel/lib/python/README.txt.in' ]),
        ('skel/log', ['skel/log/README.txt']),
        ('skel/Products', ['skel/Products/__init__.py',
                           'skel/Products/README.txt',
                          ]),
        ('skel/var', ['skel/var/README.txt']),
      ],

      ext_modules=[

        # AccessControl
        Extension(
              name='AccessControl.cAccessControl',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=['lib/python/AccessControl/cAccessControl.c'],
              depends=['include/ExtensionClass/ExtensionClass.h',
                       'include/ExtensionClass/pickle/pickle.c',
                       'include/Acquisition/Acquisition.h']),

        # DocumentTemplate
        Extension(
              name='DocumentTemplate.cDocumentTemplate',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=['lib/python/DocumentTemplate/cDocumentTemplate.c']),

        Extension(
              name='MultiMapping._MultiMapping',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=["lib/python/MultiMapping/_MultiMapping.c"],
              depends=["include/ExtensionClass/ExtensionClass.h"]),
        Extension(
              name='ThreadLock._ThreadLock',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=["lib/python/ThreadLock/_ThreadLock.c"],
              depends=["include/ExtensionClass/ExtensionClass.h"]),
        Extension(
              name='Missing._Missing',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=["lib/python/Missing/_Missing.c"],
              depends=["include/ExtensionClass/ExtensionClass.h"]),
        Extension(
              name='Record._Record',
              include_dirs=EXTENSIONCLASS_INCLUDEDIRS,
              sources=["lib/python/Record/_Record.c"],
              depends=["include/ExtensionClass/ExtensionClass.h"]),

        # initgroups
        Extension(
              name='initgroups._initgroups',
              sources=['lib/python/initgroups/_initgroups.c']),

        # indexes
        Extension(
              name='Products.PluginIndexes.TextIndex.Splitter.'
                   'ZopeSplitter.ZopeSplitter',
              sources=['lib/python/Products/PluginIndexes/TextIndex/Splitter/'
                       'ZopeSplitter/src/ZopeSplitter.c']),
        Extension(
              name='Products.PluginIndexes.TextIndex.Splitter.'
                   'ISO_8859_1_Splitter.ISO_8859_1_Splitter',
              sources=['lib/python/Products/PluginIndexes/TextIndex/Splitter/'
                       'ISO_8859_1_Splitter/src/ISO_8859_1_Splitter.c']),
        Extension(
              name='Products.PluginIndexes.TextIndex.Splitter.'
                   'UnicodeSplitter.UnicodeSplitter',
              sources=['lib/python/Products/PluginIndexes/TextIndex/Splitter/'
                       'UnicodeSplitter/src/UnicodeSplitter.c']),
        Extension(
              name='Products.ZCTextIndex.stopper',
              sources=['lib/python/Products/ZCTextIndex/stopper.c']),
        Extension(
              name='Products.ZCTextIndex.okascore',
              sources=['lib/python/Products/ZCTextIndex/okascore.c']),
      ],

      install_requires=['Acquisition==2.11.1',
                        'DateTime==2.11.1',
                        'docutils==0.4.0',
                        'ExtensionClass==2.11.1',
                        'Interface==2.11.1',
                        'Persistence==2.11.1',
                        'pytz==2007f',             # latest is fine?
                        'RestrictedPython==3.4.2',
                        'StructuredText==2.11.1',
                        'tempstorage==2.11.1',
                        'ZConfig==2.5.1',
                        'zLOG==2.11.1',
                        'zdaemon==2.0.1',
                        'ZODB3==3.8.0',
                        'zodbcode==3.4.0',
                        'zope.annotation==3.4.0',
                        'zope.cachedescriptors==3.4.0',
                        'zope.component==3.4.0',
                        'zope.configuration==3.4.0',
                        'zope.contentprovider==3.4.0',
                        'zope.contenttype==3.4.0',
                        'zope.copypastemove==3.4.0',
                        'zope.datetime==3.4.0',
                        'zope.decorator==3.4.0',
                        'zope.deferredimport==3.4.0',
                        'zope.deprecation==3.4.0',
                        'zope.documenttemplate==3.4.0',
                        'zope.dottedname==3.4.0',
                        'zope.dublincore==3.4.0',
                        'zope.error==3.5.1',
                        'zope.event==3.4.0',
                        'zope.exceptions==3.4.0',
                        'zope.filerepresentation==3.4.0',
                        'zope.formlib==3.4.0',
                        'zope.hookable==3.4.0',
                        'zope.i18nmessageid==3.4.0',
                        'zope.i18n==3.4.0',
                        'zope.index==3.4.0',
                        'zope.interface==3.4.0',
                        'zope.lifecycleevent==3.4.0',
                        'zope.location==3.4.0',
                        'zope.minmax==1.0',
                        'zope.modulealias==3.4.0',
                        'zope.pagetemplate==3.4.0',
                        'zope.proxy==3.4.0',
                        'zope.publisher==3.4.3',
                        'zope.rdb==3.4.0',
                        'zope.schema==3.4.0',
                        'zope.security==3.4.0',
                        'zope.sequencesort==3.4.0',
                        'zope.sendmail==3.4.0',
                        'zope.server==3.4.1',
                        'zope.session==3.4.1',
                        'zope.size==3.4.0',
                        'zope.securitypolicy==3.4.0',
                        'zope.structuredtext==3.4.0',
                        'zope.tales==3.4.0',
                        'zope.tal==3.4.0',
                        'zope.testbrowser==3.4.0',
                        'zope.testing==3.4.0',
                        'zope.thread==3.4.0',
                        'zope.traversing==3.4.0',
                        'zope.viewlet==3.4.0',
                        'zope.wfmc==3.4.0',
                        'zope.app.annotation==3.4.0',
                        'zope.app.apidoc==3.4.3',
                        'zope.app.applicationcontrol==3.4.1',
                        'zope.app.appsetup==3.4.1',
                        'zope.app.authentication==3.4.1',
                        'zope.app.basicskin==3.4.0',
                        'zope.app.broken==3.4.0',
                        'zope.app.cache==3.4.0',
                        'zope.app.component==3.4.1',
                        'zope.app.container==3.5.3',
                        'zope.app.content==3.4.0',
                        #'zope.app.content_types==3.4.0',       XXX
                        'zope.app.debug==3.4.0',
                        'zope.app.dependable==3.4.0',
                        'zope.app.error==3.5.1',
                        #'zope.app.event==3.4.0',               XXX
                        'zope.app.exception==3.4.1',
                        'zope.app.file==3.4.2',
                        #'zope.app.filerepresentation==3.4.0',  XXX
                        'zope.app.folder==3.4.0',
                        'zope.app.form==3.4.1',
                        'zope.app.generations==3.4.1',
                        'zope.app.http==3.4.1',
                        'zope.app.i18n==3.4.4',
                        'zope.app.interface==3.4.0',
                        'zope.app.intid==3.4.1',
                        'zope.app.keyreference==3.4.1',
                        'zope.app.layers==3.4.0',
                        'zope.app.locales==3.4.0',
                        #'zope.app.location==3.4.0',            XXX
                        #'zope.app.mail==3.4.0',                XXX
                        'zope.app.onlinehelp==3.4.0',
                        'zope.app.pagetemplate==3.4.0',
                        'zope.app.pluggableauth==3.4.0',
                        'zope.app.preference==3.4.1',
                        'zope.app.preview==3.4.0',
                        'zope.app.principalannotation==3.4.0',
                        'zope.app.publication==3.4.2',
                        'zope.app.publisher==3.4.1',
                        #'zope.app.rdb==3.4.0',                 XXX
                        'zope.app.renderer==3.4.0',
                        'zope.app.rotterdam==3.4.1',
                        'zope.app.schema==3.4.0',
                        'zope.app.security==3.4.0',
                        #'zope.app.securitypolicy==3.4.6',      XXX dep. issues
                        #'zope.app.servicnames==3.4.0',         XXX
                        'zope.app.session==3.5.1',
                        #'zope.app.site==3.4.0',                XXX
                        #'zope.app.size==3.4.0',                XXX
                        'zope.app.skins==3.4.0',
                        'zope.app.sqlscript==3.4.1',
                        'zope.app.testing==3.4.1',
                        'zope.app.traversing==3.4.0',
                        'zope.app.tree==3.4.0',
                        'zope.app.undo==3.4.0',
                        'zope.app.wfmc==0.1.2',
                        'zope.app.wsgi==3.4.0',
                        'zope.app.xmlrpcintrospection==3.4.0',
                        'zope.app.zapi==3.4.0',
                        'zope.app.zcmlfiles==3.4.3',
                        'zope.app.zopeappgenerations==3.4.0',
                        'zope.app.zptpage==3.4.1',
                        ],
      include_package_data=True,
      zip_safe=False,
      )
