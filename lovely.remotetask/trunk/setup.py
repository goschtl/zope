#!python
from setuptools import setup, find_packages
import os.path


def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names)).read()


setup(
    name='lovely.remotetask',
    version = '0.5.1',
    author="Lovely Systems",
    author_email="office@lovelysystems.com",
    description="A remotetask client utiltiy for zope 3",
    long_description=(
        read('src', 'lovely', 'remotetask', 'README.txt')
        + '\n\n'
        + read('CHANGES.txt')),
    license = "ZPL 2.1",
    keywords = "zope3 zope remotetask cache ram",
    url = 'http://pypi.python.org/pypi/lovely.remotetask',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'': 'src'},
    namespace_packages = ['lovely'],
    zip_safe = False,
    extras_require = dict(test = ['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.app.authentication',
                                  'zope.app.component',
                                  'zope.app.folder',
                                  'zope.login',
                                  'zope.securitypolicy',
                                  'zope.testbrowser',
                                  ]),
    install_requires = ['setuptools',
                        'ZODB3',
                        #'BTrees',
                        #'persistent',
                        'zc.queue',
                        'zc.table',
                        'transaction',
                        'zope.browserpage',
                        'zope.configuration',
                        'zope.location',
                        'zope.session',
                        'zope.app.container',
                        'zope.app.appsetup',
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
                        'zope.interface',
                        'zope.publisher >= 3.12.0',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing'
                        ],
    )
