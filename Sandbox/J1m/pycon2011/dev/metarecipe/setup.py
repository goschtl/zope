from setuptools import setup
setup(
    name = 'cmsappdbmetarecipe',
    py_modules = ['cmsappdbmetarecipe'],
    entry_points = {'zc.buildout': ['default = cmsappdbmetarecipe:MetaRecipe']},
    install_requires = ['setuptools'],
    zip_safe = False,
    )
