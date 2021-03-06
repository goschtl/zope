#!python
from setuptools import setup, find_packages

setup (
    name='lovely.remotetask',
    version='0.2.12',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A remotetask client utiltiy for zope 3",
    license = "ZPL 2.1",
    keywords = "zope3 zope remotetask cache ram",
    url = 'svn://svn.zope.org/repos/main/lovely.remotetask',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    zip_safe = False,
    extras_require = dict(test = ['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  "zope.app.server",
                                  'zope.testbrowser',
                                  ]),
    install_requires = ['setuptools',
                        'ZODB3',
                        'zc.queue',
                        'zc.table',
                        'zope.app.container',
                        'zope.app.generations',
                        'zope.app.pagetemplate',
                        'zope.app.publication',
                        'zope.app.publisher',
                        # We depend on zope.app.session, but
                        # import from zope.session if available,
                        # to avoid deprecation warnings.
                        'zope.app.session',
                        'zope.app.xmlrpcintrospection',
                        'zope.component',
                        'zope.formlib',
                        'zope.interface',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing'
                        ],
    )
