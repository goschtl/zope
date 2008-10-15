from setuptools import setup, find_packages

YUI_VERSION = '2.6.0'

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )


setup(
    name='hurry.yui',
    version=YUI_VERSION + '.2' + 'dev',
    description="hurry.resource style resources for YUI.",
    long_description = long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource > 0.2',
        'simplejson',
        ],
    entry_points= {
    'console_scripts': [
      'yuiprepare = hurry.yui.prepare:main',
      ]
    },

    )
