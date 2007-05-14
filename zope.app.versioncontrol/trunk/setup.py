from setuptools import setup, find_packages

setup(
    name = 'zope.app.versioncontrol',
    version = '0.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    extras_require=dict(test=['zope.event',
                              'zope.traversing',
                              'zope.annotation>=3.4.0b1.dev-r75055', 
                              'zope.component']),
    install_requires = ['setuptools',
                        'ZODB3',
                        'zope.location',
                        'zope.security'],
    zip_safe = False,
    )
