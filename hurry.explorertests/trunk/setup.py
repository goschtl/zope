from setuptools import setup, find_packages

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = ''
#(
#    read('README.txt')
#    + '\n' +
#    read('CHANGES.txt')
#    + '\n' +
#    'Download\n'
#    '********\n'
#    )


setup(
    name='hurry.explorertests',
    version='0.1dev',
    description="Javascript based tests for hurry.explorer. Uses grok for JSON",
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
        'grok',
        'z3c.objpath',
        'grokui.admin',
        'hurry.zoperesource',
        'hurry.yui >= 2.6.0.3',
        'hurry.zopeyui',
        'hurry.explorer',
        ],
    )
