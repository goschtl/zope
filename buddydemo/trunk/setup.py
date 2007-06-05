from setuptools import setup, find_packages

setup(
    name = 'buddydemo',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.interface',
                        'zope.event',
                        'zope.lifecycleevent',
                        'ZODB3',
                        'zope.app.zapi',
                        'zope.app.container',
                        'zope.component',
                        'zope.publisher',
                        'zope.schema',
                       ],
    extras_require=dict(test=['zope.app.testing',
                              'zope.app.zcmlfiles',
                              'zope.app.securitypolicy']),
    zip_safe = False,
    )
