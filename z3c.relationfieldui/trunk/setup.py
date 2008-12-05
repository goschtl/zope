from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'z3c', 'relationfieldui', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='z3c.relationfieldui',
    version='0.2dev',
    description="A widget for z3c.relationfield.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'z3c.relationfield',
        'z3c.schema2xml >= 1.0',
        'grokcore.component',
        'grokcore.view',
        'hurry.resource',
        'hurry.zoperesource >= 0.3', # for testing
        ],
    entry_points={},
    )
