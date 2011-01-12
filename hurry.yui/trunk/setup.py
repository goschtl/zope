from setuptools import setup, find_packages

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
    version='2.7.0.1',
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
        'hurry.resource > 0.9',
        'simplejson',
        ],
    entry_points= {
        'console_scripts': [
            'yuiprepare = hurry.yui.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.yui.prepare:working_entrypoint',
            ],
        'zest.releaser.releaser.after_checkout': [
            'prepare = hurry.yui.prepare:tag_entrypoint',
            ],
        'hurry.resource.libraries': [
            'yui = hurry.yui:yui',
            ],
        },

    )
