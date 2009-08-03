from setuptools import setup, find_packages


setup(
    name='z3c.recipe.kgs',
    version='0.1dev',
    author='Fabio Tranchitella',
    author_email='fabio@tranchitella.it',
    description='Buildout recipe to create testrunners for testing compatibility with packages from a KGS',
    url='http://pypi.python.org/pypi/z3c.recipe.kgs',
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()),
    keywords="zope3 setuptools egg kgs",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Zope3'],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c', 'z3c.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'zc.recipe.testrunner',
        'zope.kgs',
    ],
    entry_points = {
        'zc.buildout': ['default = z3c.recipe.kgs.recipe:Recipe'],
    },
    include_package_data=True,
    zip_safe=False,
)
