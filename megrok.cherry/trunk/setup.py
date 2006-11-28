from setuptools import setup, find_packages

setup(
    name='megrok.cherry',
    version='0.1',
    author='Startifact',
    author_email='faassen@startifact.com',
    description="""\
Using Zope Grok with CherryPy.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='BSD',
   entry_points= {
    'console_scripts': [   
      'startserver = megrok.cherry.server:startServer',
      ]
    },
    install_requires=[
    'CherryPy',
    'grok',
    'setuptools',
    ],
)
