#!python
from setuptools import setup, find_packages
import os.path


def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names)).read()


setup (
    name='lovely.remotetask',
    version = '0.6dev',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A remotetask client utiltiy for zope 3",
    long_description=(
        read('src', 'lovely', 'remotetask', 'README.txt')
        + '\n\n'
        + read('CHANGES.txt')),
    license = "ZPL 2.1",
    keywords = "zope3 zope remotetask cache ram",
    url = 'http://pypi.python.org/pypi/lovely.remotetask',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    zip_safe = False,
    extras_require = dict(test = ['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.securitypolicy',
                                  'zope.app.authentication',
                                  'zope.app.folder',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser',
                                  ],
                          zope2 = ['Acquisition',
                                   #'Products.five',
                                   #'ZPublisher',
                          ]),
    install_requires = ['setuptools',
                        'ZODB3',
                        #'BTrees',
                        #'transaction',
                        'zc.queue',
                        'zc.table',
                        'zope.app.appsetup',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.form',
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
                        'zope.configuration',
                        'zope.formlib',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.session',
                        'zope.traversing'
                        ],
    )
