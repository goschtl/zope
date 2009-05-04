from setuptools import setup, find_packages
import sys, os, shutil, tempfile

EXTJS_VERSION = '2.2.1'

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
    name='hurry.extjs',
    version= EXTJS_VERSION,
    description="ExtJS for hurry.resource.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Santiago Videla',
    author_email='santiago.videla@gmail.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource',
        ],
    entry_points= {
    },

    )
