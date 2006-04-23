from setuptools import setup, find_packages

setup(
    name = 'notzipsafe',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize=notzipsafe:initialize']},
    url = 'http://www.example.com/notzipsafe',
    package_data = {'':['*.jpg']},
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    zip_safe = False,
    )
