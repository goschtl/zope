from setuptools import setup, find_packages
import os

SLIMBOX_VERSION = '2.03'
version = '2.03'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='hurry.slimbox',
    version=version,
    description="hurry.resource style resources for Slimbox.",
    long_description=long_description,
    classifiers=[],
    keywords='jQuery Slimbox Zope3 Popup',
    author='Souheil Chelfouh',
    author_email='trollfot@gmail.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.jquery',
        'hurry.resource >= 0.4.1',
        ],
    entry_points={
        'console_scripts': [
            'slimboxprepare = hurry.slimbox.prepare:main',
            ],
        'zest.releaser.prereleaser.middle': [
            'prepare = hurry.slimbox.prepare:entrypoint',
            ],
        # ALSO grab slimbox in the separate tag checkout...
        'zest.releaser.releaser.middle': [
            'prepare = hurry.slimbox.prepare:entrypoint',
            ],
        },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
