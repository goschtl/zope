from setuptools import setup, find_packages

setup(
    name = 'z3c.optionstorage',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'persistent',
                        'zope.annotation',
                        'zope.configuration', 
                        'zope.deprecation', 
                        'zope.i18n',
                        'zope.interface',
                        'zope.proxy',
                        'zope.app.schema',
                        'zope.schema',
                        'zope.security',
                        'zope.app.pagetemplate',
                        'zope.app.publisher',
                        'zope.app.form',
                        'zope.app.zapi'],
    zip_safe = False,
    )
