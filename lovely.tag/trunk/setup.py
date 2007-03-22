#!python
from setuptools import setup, find_packages

setup (
    name='lovely.tag',
    version='0.2',
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
        test = ['z3c.sampledata']
        ),
    install_requires = [
        'setuptools',
        'zope.interface',
        'zope.component',
        'ZODB3',
        'zope.app.container',
        'zope.i18nmessageid',
        ],
    dependency_links = ['http://download.zope.org/distribution']
    )

