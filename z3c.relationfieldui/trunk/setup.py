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
    version='0.6dev',
    description="A widget for z3c.relationfield.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'z3c.relationfield >= 0.4',
        'z3c.schema2xml >= 1.0',
        'zc.sourcefactory',
        'grokcore.component',
        'grokcore.view',
        'hurry.resource < 0.9',
        # for testing:
        'hurry.zoperesource >= 0.3, <0.6',
        'zope.app.testing',
        ],
    entry_points={},
    )
