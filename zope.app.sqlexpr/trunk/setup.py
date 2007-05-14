from setuptools import setup, find_packages

setup(
    name = 'zope.app.sqlexpr',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.component',
                        'zope.interface',
                        'zope.tales',
                        'zope.exceptions',
                        'zope.rdb'],
    extras_require=dict(test=['zope.app.sqlexpr']),
    zip_safe = False,
    )
