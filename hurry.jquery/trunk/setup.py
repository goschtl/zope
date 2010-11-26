from setuptools import setup, find_packages
import os

JQUERY_VERSION = '1.4.3'
version = '1.4.3.2dev'
# Name version after JQUERY_VERSION + .suffix


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n')

setup(
    name='hurry.jquery',
    version=version,
    description="fanstatic style resources for jQuery.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Jan-Wijbrand Kolman',
    author_email='jw@n--tree.net',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'fanstatic',
        ],
    entry_points={
        'console_scripts': [
            'jqueryprepare = hurry.jquery.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.jquery.prepare:working_entrypoint',
            ],
        'zest.releaser.releaser.after_checkout': [
            'prepare = hurry.jquery.prepare:tag_entrypoint',
            ],
        'fanstatic.libraries': [
            'jquery = hurry.jquery:jquery_lib',
            ],
        },
    )
