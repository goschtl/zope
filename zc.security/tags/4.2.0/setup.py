from setuptools import setup, find_packages

setup(
    name = 'zc.security',
    version = '4.2.0',
    author = 'Zope Corporation',
    author_email = 'zope3-dev@zope.org',
    description = 'Principal-searching UI for Zope 3 Pluggable Authentication',
    license = 'ZPL 2.1',
    keywords = 'zope3 security',
    url='http://svn.zope.org/zc.sharing',
    classifiers = [
        'License :: OSI Approved :: Zope Public License',
        ],

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'': 'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'setuptools',
       'zope.app.authentication',
       'zope.app.component',
       'zope.app.security',
       'zope.component',
       'zope.interface',
       'zope.security',
       'zope.testing',
       ],
    )
