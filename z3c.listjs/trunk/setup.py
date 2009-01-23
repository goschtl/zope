from setuptools import setup, find_packages
import sys, os

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
    name='z3c.listjs',
    version='1.0a3dev',
    description="A formlib list widget that uses Javascript",
    long_description=long_description,
    keywords='zope3 form widget',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.schema',
        'zope.app.form',
        'grokcore.component',
        'hurry.resource',
        'hurry.zoperesource >= 0.3',
        ],
    entry_points={},
    )
