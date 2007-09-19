import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.fssync',
    version = '3.4.0b1',
    url='http://svn.zope.org/zope.app.fssync',
    license='ZPL 2.1',
    description='Zope app fssync',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    long_description="Filesystem synchronization for Zope 3 Applications.",
    
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    
    namespace_packages=['zope',],
    tests_require = ['zope.testing'],
    extras_require = dict(
        app = ['zope.app.appsetup',
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
               ]
              ),
    install_requires=['setuptools',
                    'zope.dublincore',
                    'zope.fssync',
                    'zope.interface',
                    'zope.proxy',
                    'zope.testbrowser',
                    'zope.traversing',
                    'zope.xmlpickle',
                    'zope.app.catalog',
                    'zope.app.component',
                    'zope.app.dtmlpage',
                    'zope.app.file',
                    'zope.app.folder',
                    'zope.app.module',
                    'zope.app.securitypolicy',
                    'zope.app.zcmlfiles',
                    'zope.app.zptpage'
                    ],
    include_package_data = True,
    
    zip_safe = False,
    )
