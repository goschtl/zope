from setuptools import setup, find_packages

name = 'zc.recipe.deployment'
setup(
    name = name,
    install_requires = ['setuptools'],
    entry_points = '[zc.buildout]\ndefault=%s:Recipe' % name,
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    namespace_packages = ['zc', 'zc.recipe']
    )

