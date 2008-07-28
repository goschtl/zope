from setuptools import setup, find_packages

setup(
    name="z3c.formsnippet",
    version="0.1",
    description="""\
This package is an addon to z3c.form, similar to z3c.formui which introduces 
an alternate concept to customizing form templates by introducing so-called
'Form Frames' and 'Widget Snippets'.
""",

    author="Hermann Himmelbauer",
    author_email="dusty@qwer.tk",

    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['z3c'], 
)
