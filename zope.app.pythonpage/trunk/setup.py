from setuptools import setup, find_packages

setup(
    name = 'zope.app.pythonpage',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    extras_require=dict(test=['zope.app.testing']),
    install_requires = ['setuptools',
                        'ZODB3',
                        'zope.app.zapi',
                        'zope.app.container',
                        'zope.app.interpreter',
                        'zope.interface',
                        'zope.schema',
                        'zope.app.i18n',
                        'zope.security'],
    zip_safe = False,
    )
