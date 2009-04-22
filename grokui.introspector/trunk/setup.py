from setuptools import setup, find_packages
import os

tests_require = ['z3c.testsetup',
                ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='grokui.introspector',
    version='0.1dev',
    author='Uli Fouquet',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://cheeseshop.python.org/pypi/grokui.introspector/',
    description='An introspector for Grok',
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
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'grok',
                      'zope.introspector',
                      'zope.introspectorui',
                      'hurry.zopeyui',
                      ],
    tests_require = tests_require,
    extras_require = dict(test=tests_require), 
)
