import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='mars.formdemo',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/mars',
    description="""\
Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

This package uses martian to reproduce and imitiate z3c.formdemo
as a experiment in using mars packages to configure zope apps""",
    long_description=(
        read('src/mars/formdemo/README.txt')
        ),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL',
    dependency_links = ['http://download.zope.org/distribution'],
    extras_require = dict(
        app = ['z3c.formdemo',
               ],
        test = ['z3c.etestbrowser',
                'zope.app.testing'],
        ),
    install_requires = [
        'setuptools',
        'grok',
        'martian',
        'lxml',
        'pytz',
        'ZODB3',
        'z3c.csvvocabulary',
        'z3c.form',
        'z3c.formui',
        'z3c.layer',
        'z3c.pagelet',
        'z3c.template',
        'z3c.viewlet',
        'z3c.zrtresource',
        'z3c.formdemo',
        'zc.resourcelibrary',
        'zc.table',
        'mars.form',
        'mars.layer',
        'mars.contentprovider',
        'mars.view',
        'mars.viewlet',
        'mars.macro',
        'mars.resource',
        'mars.template',
        'mars.adapter',
        ],
)
