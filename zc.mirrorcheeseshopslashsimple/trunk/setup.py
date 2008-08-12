from setuptools import setup

setup(
    name='zc.mirrorcheeseshopslashsimple',
    version='0.3',
    description='A script for mirroring the PyPI simple index',
    package_dir = {'': 'src'},
    install_requires = ['zc.lockfile'],
    entry_points = dict(console_scripts=[
        'update-simple-mirror = zc.mirrorcheeseshopslashsimple:update',
        ])
    )
