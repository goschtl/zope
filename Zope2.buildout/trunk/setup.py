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
      version = '2.12.dev',
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

      install_requires=['Acquisition',
                        'DateTime',
                        'docutils',
                        'ExtensionClass',
                        'Interface',
                        'Persistence',
                        'pytz',
                        'RestrictedPython',
                        'StructuredText',
                        'tempstorage',
                        'ZConfig',
                        'zLOG',
                        'zdaemon',
                        'ZODB3',
                        'zodbcode',
                        'zope.annotation',
                        'zope.cachedescriptors',
                        'zope.component',
                        'zope.configuration',
                        'zope.contentprovider',
                        'zope.contenttype',
                        'zope.copypastemove',
                        'zope.datetime',
                        'zope.decorator',
                        'zope.deferredimport',
                        'zope.deprecation',
                        'zope.documenttemplate',
                        'zope.dottedname',
                        'zope.dublincore',
                        'zope.error',
                        'zope.event',
                        'zope.exceptions',
                        'zope.filerepresentation',
                        'zope.formlib',
                        'zope.hookable',
                        'zope.i18nmessageid',
                        'zope.i18n',
                        'zope.index',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.location',
                        'zope.minmax',
                        'zope.modulealias',
                        'zope.pagetemplate',
                        'zope.proxy',
                        'zope.publisher',
                        'zope.rdb',
                        'zope.schema',
                        'zope.security',
                        'zope.sequencesort',
                        'zope.sendmail',
                        'zope.server',
                        'zope.session',
                        'zope.size',
                        'zope.securitypolicy',
                        'zope.structuredtext',
                        'zope.tales',
                        'zope.tal',
                        'zope.testbrowser',
                        'zope.testing',
                        'zope.thread',
                        'zope.traversing',
                        'zope.viewlet',
                        'zope.wfmc',
                        'zope.app.annotation',
                        'zope.app.apidoc',
                        'zope.app.applicationcontrol',
                        'zope.app.appsetup',
                        'zope.app.authentication',
                        'zope.app.basicskin',
                        'zope.app.broken',
                        'zope.app.cache',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.content',
                        #'zope.app.content_types==3.4.0',       XXX
                        'zope.app.debug',
                        'zope.app.dependable',
                        'zope.app.error',
                        #'zope.app.event==3.4.0',               XXX
                        'zope.app.exception',
                        'zope.app.file',
                        #'zope.app.filerepresentation==3.4.0',  XXX
                        'zope.app.folder',
                        'zope.app.form',
                        'zope.app.generations',
                        'zope.app.http',
                        'zope.app.i18n',
                        'zope.app.interface',
                        'zope.app.intid',
                        'zope.app.keyreference',
                        'zope.app.layers',
                        'zope.app.locales',
                        #'zope.app.location==3.4.0',            XXX
                        #'zope.app.mail==3.4.0',                XXX
                        'zope.app.onlinehelp',
                        'zope.app.pagetemplate',
                        'zope.app.pluggableauth',
                        'zope.app.preference',
                        'zope.app.preview',
                        'zope.app.principalannotation',
                        'zope.app.publication',
                        'zope.app.publisher',
                        #'zope.app.rdb==3.4.0',                 XXX
                        'zope.app.renderer',
                        'zope.app.rotterdam',
                        'zope.app.schema',
                        'zope.app.security',
                        #'zope.app.securitypolicy==3.4.6',      XXX dep. issues
                        #'zope.app.servicnames==3.4.0',         XXX
                        'zope.app.session',
                        #'zope.app.site==3.4.0',                XXX
                        #'zope.app.size==3.4.0',                XXX
                        'zope.app.skins',
                        'zope.app.sqlscript',
                        'zope.app.testing',
                        'zope.app.traversing',
                        'zope.app.tree',
                        'zope.app.undo',
                        'zope.app.wfmc',
                        'zope.app.wsgi',
                        'zope.app.xmlrpcintrospection',
                        'zope.app.zapi',
                        'zope.app.zcmlfiles',
                        'zope.app.zopeappgenerations',
                        'zope.app.zptpage',
                        ],
      include_package_data=True,
      zip_safe=False,
      )
