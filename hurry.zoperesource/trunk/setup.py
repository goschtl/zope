from setuptools import setup, find_packages
import sys, os

setup(
    name='hurry.zoperesource',
    version='0.1dev',
    description="Flexible resources for Zope.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='',
    packages=find_packages('src'),
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
        'hurry.resource',
        ],
    entry_points={},
    )
