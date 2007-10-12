import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "z3c.recipe.dev"
setup(
    name = name,
    version = "0.0.1dev",
    author = "Roger Ineichen and the Zope Community",
    author_email = "roger@projekt01.ch",
    description = "Zope3 development recipes",
    long_description = (
        read('README.txt')
         + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'z3c', 'recipe', 'dev', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c dev recipe",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://cheeseshop.python.org/pypi/'+name,
    packages = find_packages('src'),
    package_dir = {'':'src'},
    dependency_links = ['http://download.zope.org/distribution/'],
    include_package_data = True,
    namespace_packages = ['z3c', 'z3c.recipe'],
    extras_require = dict(
        test = [
            'zc.recipe.filestorage',
            ],
        ),
    install_requires = [
        'ZConfig >=2.4a5',
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'zope.testing',
        ],
    entry_points = {
        'zc.buildout': [
             'app = %s.app:AppSetup' % name,
             'script = %s.script:ScriptSetup' % name,
         ]
    },
)
