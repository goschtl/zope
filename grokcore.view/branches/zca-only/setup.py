from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

install_requires = [
    'setuptools',
    'grokcore.component >= 2.1',
    'grokcore.security >= 1.5',
    'martian >= 0.13',
    'zope.component',
    'zope.interface',
    'zope.pagetemplate',
    'zope.publisher',
    'zope.security',
    'zope.traversing',
    ]

tests_require = [
    'zope.container',
    'zope.securitypolicy',
    'zope.site',
    'zope.browserpage',
    'zope.principalregistry',
    ]

setup(
    name='grokcore.view',
    version='3.0dev',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grok/',
    description='Grok-like configuration for Zope browser pages',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
