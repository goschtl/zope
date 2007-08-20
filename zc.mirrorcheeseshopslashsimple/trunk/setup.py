from setuptools import setup

setup(
    name='ppix',
    version='0.2',
    package_dir = {'': 'src'},
    install_requires = ['zc.lockfile'],
    entry_points = dict(console_scripts=[
        'update-simple-mirror = zc.mirrorcheeseshopslashsimple:update',
        ])
    )
