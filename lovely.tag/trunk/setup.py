#!python
from setuptools import setup, find_packages

setup (
    name='lovely.tag',
    version='0.3',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A tagging engine for zope 3",
    license = "ZPL 2.1",
    keywords = "zope3 web20 zope tagging",
    url = 'svn://svn.zope.org/repos/main/lovely.tag',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.app.catalog',
                'z3c.sampledata']
        ),
    install_requires = [
        'setuptools',
        'ZODB3',
        'pytz',
        'z3c.configurator',
        'zope.app.component',
        'zope.app.container',
        'zope.app.folder',
        'zope.app.generations',
        'zope.app.intid',
        'zope.app.pagetemplate',
        'zope.app.zopeappgenerations',
        'zope.cachedescriptors',
        'zope.component',
        'zope.dottedname',
        'zope.formlib',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.security'
        ],
    dependency_links = ['http://download.zope.org/distribution']
    )

