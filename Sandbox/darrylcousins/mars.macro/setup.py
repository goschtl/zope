import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='mars.macro',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/mars',
    description="""\
Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

This package uses martian to register macros.""",
    long_description=(
        read('src/mars/macro/README.txt')
        ),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL',
    dependency_links = ['http://download.zope.org/distribution'],
    extras_require = dict(
        test = ['zope.app.appsetup',
               'zope.app.authentication',
               'zope.app.component',
               'zope.app.container',
               'zope.app.error',
               'zope.app.form',
               'zope.app.publisher',
               'zope.app.publication',
               'zope.app.security',
               'zope.app.securitypolicy',
               'zope.app.twisted',
               'zope.app.wsgi',
               'zope.contentprovider',
               'zope.app.intid',
                'z3c.formdemo',
                'z3c.etestbrowser',
                'zope.app.zcmlfiles',
                'zope.app.testing',
                'mars.template'],
        ),
    install_requires = [
        'setuptools',
        'simplejson',
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
        'zope.annotation',
                      'zope.app.catalog',
                      'zope.app.folder',
        'zope.app.container',
        'zope.app.pagetemplate',
        'zope.app.session',
        'zope.component',
        'zope.interface',
        'zope.location',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.rdb',
        'zope.schema',
        'zope.traversing',
        'zope.viewlet',
        ],
)
        #              'zope.app.pagetemplate',
        #              'zope.app.testing',
        #              'zope.configuration',
        #              'zope.dottedname',
        #              'zope.event',
        #              'zope.formlib',
        #              'zope.lifecycleevent',
        #              'zope.security',
        #              'zope.testing',


