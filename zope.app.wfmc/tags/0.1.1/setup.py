from setuptools import setup, find_packages

setup(
    name = 'zope.app.wfmc',
    version = '0.1.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    package_data = {'': ['*.txt', '*.zcml', '*.xpdl']},
    extras_require=dict(test=['zope.app.testing']),
    install_requires = ['setuptools',
                       'zope.interface',
                       'zope.schema',
                       'zope.configuration',
                       'zope.wfmc',
                       'zope.component'],
    zip_safe = False,
    )
