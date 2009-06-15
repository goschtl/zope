from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'hurry', 'custom', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )

setup(
    name="hurry.custom",
    version = '0.6.1',
    description="A framework for allowing customizing templates",
    long_description=long_description,    
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='template custom templating customization',
    author='Martijn Faassen, Startifact',
    author_email='faassen@startifact.com',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir= {'':'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
       'setuptools',
       'zope.component',
       'zope.interface',
       'zope.hookable',
       'jsontemplate',
       'zope.configuration',
       ],
    )
