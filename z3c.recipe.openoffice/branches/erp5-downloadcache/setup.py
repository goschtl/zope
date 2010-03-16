from setuptools import setup, find_packages
import os

version = '0.3'
name='z3c.recipe.openoffice'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    author="Infrae",
    author_email="faassen@infrae.com",
    description="zc.buildout recipe that downloads and installs OpenOffice.org",
    long_description=(read('README.txt')),
    license='ZPL 2.1',
    keywords = "buildout openoffice",
    url='http://svn.zope.org/z3c.recipe.openoffice',

    packages=find_packages('src'),
    include_package_data=True,
    package_dir = {'': 'src'},
    namespace_packages=['z3c', 'z3c.recipe'],
    install_requires=['zc.buildout', 'setuptools'],
    entry_points={'zc.buildout': ['default = %s.recipe:Recipe' % name]},
    zip_safe=False,
    )
