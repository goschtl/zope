from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(
    name='grokcore.view',
    version='1.1dev',
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
    install_requires=['setuptools',
                      'martian >= 0.10',
                      'grokcore.component >= 1.5.1',
                      'grokcore.security',
                      'zope.schema',
                      'zope.security',
                      'zope.traversing',
                      'zope.app.publisher',
                      'zope.app.pagetemplate',
                      # for ftests:
                      # TODO move these to extra_requires?
                      'zope.testbrowser',
                      'zope.securitypolicy',
                      'zope.app.zcmlfiles',
                      'zope.app.authentication',
                      ],
)
