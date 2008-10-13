from setuptools import setup, find_packages
import sys, os

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
    version='0.2',
    description="hurry.resource integration for Zope.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'z3c.autoinclude',
        'grokcore.component',
        'zope.security',
        'zope.publisher',
        'zope.app.component',
        'zope.traversing',
        'zope.securitypolicy',
        'zope.testbrowser',
        'hurry.resource > 0.1',
        ],
    entry_points={},
    )
