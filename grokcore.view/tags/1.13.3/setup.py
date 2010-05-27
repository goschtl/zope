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
    'grokcore.component >= 1.5',
    'grokcore.security >= 1.2',
    'martian >= 0.10',
    'zope.browserresource >= 3.9.0',
    'zope.component',
    'zope.interface',
    'zope.login',
    'zope.pagetemplate',
    'zope.ptresource >= 3.9.0',
    'zope.publisher',
    'zope.security',
    'zope.traversing',
    ]

tests_require = [
    'zope.app.wsgi [test]',
    'zope.configuration',
    'zope.container',
    'zope.site',
    'zope.testing',
    ]

setup(
    name='grokcore.view',
    version = '1.13.3',
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
    tests_require = tests_require,
    install_requires = install_requires,
    extras_require = {'test': tests_require},
)
