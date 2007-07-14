#!python
from setuptools import setup, find_packages

setup(
    name = 'z3c.responseheaders',
    version = '0.1.0',
    author = "Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "Adds adaptable response cache header settings",
    license = "ZPL 2.1",
    keywords = "zope zope3",
    url='http://svn.zope.org//z3c.responseheaders',
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir = {'':'src'},
    namespace_packages=['z3c',],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.traversing',
        ],
    extras_require = dict(
    test = ['zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.testbrowser']
    ),
)

