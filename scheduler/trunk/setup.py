from setuptools import setup, find_packages

setup(
    name = 'scheduler',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    extras_require = dict(test=['zope.app.testing']),
    zip_safe = False,
    )
