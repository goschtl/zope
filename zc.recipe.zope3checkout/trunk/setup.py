from setuptools import setup, find_packages
import os.path

name = "zc.recipe.zope3checkout"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = name,
    version = "1.2",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for installing a Zope 3 checkout",
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,
    classifiers = [
        'License :: OSI Approved :: Zope Public License',
        ],

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc', 'zc.recipe'],
    install_requires = ['setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
