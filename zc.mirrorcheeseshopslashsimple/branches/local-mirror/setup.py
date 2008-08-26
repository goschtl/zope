from setuptools import setup

CLASSIFIERS = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Zope Public License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
]

long_desc = open('README.txt').read()

setup(
    name='zc.mirrorcheeseshopslashsimple',
    version='0.4',
    description='A script for mirroring the PyPI simple index',
    license='ZPL (see LICENSE.txt)',
    author='Jim Fulton',
    author_email='jim@zope.com',
    maintainer='Jim Fulton',
    maintainer_email='jim@zope.com',
    classifiers=CLASSIFIERS,
    long_description=long_desc,
    package_dir = {'': 'src'},
    install_requires = ['zc.lockfile'],
    entry_points = dict(console_scripts=[
        'update-simple-mirror = zc.mirrorcheeseshopslashsimple:update',
        ])
    )
