from setuptools import setup, find_packages

setup(
    name="z3c.hroles",
    version="0.1",
    description = "This package provides hierarchical roles for Zope 3. "
    "This way roles can automatically include other roles.",
    author="Hermann Himmelbauer",
    author_email="dusty@qwer.tk",

    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['z3c'], 
)
