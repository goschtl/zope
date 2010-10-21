from setuptools import setup, find_packages
import os.path


def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text + '\n\n'


setup(
    name = "z3c.sessionwidget",
    version = "0.1dev",
    author = "Zope Contributors",
    author_email = "zope3-dev@zope.org",
    description = "Session Input Widget",
    long_description=(
        '.. contents::\n\n' +
        read('CHANGES.txt') +
        read('src', 'z3c', 'sessionwidget', 'README.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 session widget",
    url = 'http://svn.zope.org/z3c.sessionwidget',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI"],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    zip_safe = False,
    extras_require = dict(test=['zope.component',
                                'zope.app.testing',
                                'zope.testing',
                                'zope.publisher',
                               ]),
    install_requires = ['setuptools',
                        'zope.app.form',
                        'zope.app.session',
                        'zope.interface',
                        'zope.location',
                        'zope.schema',
                        'zope.security',
                        ],
    )
