from setuptools import setup, find_packages

setup(
    name = 'zope.app.schemacontent',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.app.i18n',
                        'zope.app.zapi',
                       'zope.app.form',
                       'zope.component',
                       'zope.interface',
                       'zope.publisher',
                       'zope.schema',
                       'zope.security',
                       'ZODB3',
                       'zope.app.container',
                       'zope.app.publisher'],
    extras_require=dict(test=['zope.app.testing', 'zope.annotation']),
    zip_safe = False,
    )
