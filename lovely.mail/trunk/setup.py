import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('src', 'lovely', 'mail', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '========\n'
        )

name = 'lovely.mail'
setup(
    name = name,
    version = '0.2.0',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    license = "ZPL 2.1",
    keywords = "mail zope zope3",
    url = 'http://launchpad.net/lovely.mail',
    description = "sending emails via remotetask",
    long_description = long_description,
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'zope.component',
                        'zope.schema',
                        'zope.sendmail',
                        'lovely.remotetask',
                        ],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',]),
    classifiers = [
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    )

