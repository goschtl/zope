from setuptools import setup, find_packages

setup(
    name = 'zope.app.styleguide',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = 'Styleguide for Zope 3 developers as a Zope 3 online help chapter',
    license = 'ZPL 2.1',

    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    zip_safe = False,
    )
