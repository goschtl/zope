from setuptools import setup, find_packages

setup(
    name = 'zope.app.zopetop',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.interface',
                        'zope.app.skins',
                        'zope.app.basicskin',
                        'zope.publisher',
                        'zope.app.rotterdam'],
    extras_require=dict(test=['zope.app.testing',
                              'zope.app.zcmlfiles',
                              'zope.app.securitypolicy',
                              'zope.app.authentication']),
    zip_safe = False,
    )
