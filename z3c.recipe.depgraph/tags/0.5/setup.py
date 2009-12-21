from setuptools import setup, find_packages


setup(
    name='z3c.recipe.depgraph',
    version = '0.5',
    author='Zope Community',
    author_email='zope-dev@zope.org',
    description='Buildout recipe to generate dependency graphs.',
    url='http://pypi.python.org/pypi/z3c.recipe.depgraph',
    long_description= (
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    keywords = "egg dependency",
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        ],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['z3c', 'z3c.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'tl.eggdeps',
        ],
    entry_points = {
        'zc.buildout': ['default = z3c.recipe.depgraph.recipe:Recipe'],
        },
    include_package_data = True,
    zip_safe = False,
)
