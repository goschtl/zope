from setuptools import setup

setup(
    name = "recipes",
    install_requires = ['zc.recipe.egg'],
    entry_points = {'zc.buildout': ['application = zope3recipes:Application']},
    )
