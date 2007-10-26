#!python
from setuptools import setup, find_packages

setup(
    name = 'z3c.traverser',
    version = '0.2.0b2',
    author = "Zope Community",
    author_email = "zope3-dev@zope.org",
    description = open("README.txt").read(),
    license = "ZPL 2.1",
    keywords = "zope zope3",
    url='http://svn.zope.org//z3c.traverser',
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir = {'':'src'},
    namespace_packages=['z3c',],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.contentprovider',
        'zope.interface',
        'zope.publisher',
        'zope.traversing',
        'zope.viewlet',
        ],
    extras_require = dict(
    test = ['zope.app.testing',
            'zope.app.securitypolicy',
            'zope.app.zcmlfiles',
            'zope.testbrowser']
    ),
)

