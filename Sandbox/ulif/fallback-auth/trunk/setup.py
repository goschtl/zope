from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'z3c', 'fallbackauth', 'README.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    )

setup(
    name='z3c.fallbackauth',
    version='0.1',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    url='',
    download_url='',
    description='A fallback authenticator plugin for Zope 3',
    long_description=long_description,
    license='ZPL',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['z3c'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'zope.app.authentication',
                      'zope.app.security',
                      'zope.interface',
                      ],
)
