#!python
from setuptools import setup, find_packages

setup (
    name='z3c.reference',
    version='1.0.0a3',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "Reference",
    license = "ZPL 2.1",
    keywords = "zope3 web20 zope reference",
    url = 'svn://svn.zope.org/repos/main/z3c.reference',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',
                'zope.testbrowser',
                'zope.app.server',
                'z3c.testing',
                'zope.app.zcmlfiles',
                'zope.app.securitypolicy']
        ),
    install_requires = [
        'setuptools',
        'ZODB3',
        'BeautifulSoup',
        'zc.resourcelibrary',
        'zope.app.component',
        'zope.app.file',
        'zope.app.form',
        'zope.app.keyreference',
        'zope.cachedescriptors',
        'zope.dublincore',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.traversing',
        'lovely.relation>=0.3.0',
        'z3c.javascript',
        'z3c.viewtemplate',
        'cElementTree',
        'elementtree'
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    zip_safe = False,    
    )
