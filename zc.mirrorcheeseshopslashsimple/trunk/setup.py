from setuptools import setup

setup(
    name='zc.mirrorcheeseshopslashsimple',
    version='0.2',
    package_dir = {'': 'src'},
    install_requires = ['zc.lockfile'],
    entry_points = dict(console_scripts=[
        'update-simple-mirror = zc.mirrorcheeseshopslashsimple:update',
        'generate-buildout = zc.mirrorcheeseshopslashsimple:generate_buildout',
        'generate-controlled-pages = \
             zc.mirrorcheeseshopslashsimple:generate_controlled_pages',
        ])
    )
