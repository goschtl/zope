from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'hurry', 'zoperesource', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.zoperesource',
    version='0.8dev',
    description="hurry.resource integration for Zope.",
    long_description=long_description,
    classifiers=['Framework :: Zope3'],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    url='http://pypi.python.org/pypi/hurry.zoperesource',
    license='ZPL',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'fanstatic',
        'z3c.autoinclude',
        'zope.browserresource',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.security',
        'zope.traversing',
        ],
    extras_require = {
      'test': [
         'zope.annotation',
         'zope.app.publication',
         'zope.app.wsgi >= 3.10.0',
         'zope.browserpage',
         'zope.container',
         'zope.principalregistry',
         'zope.securitypolicy',
         'zope.site',
         'zope.app.appsetup',
         ],
      },
    )
