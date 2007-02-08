from setuptools import setup, find_packages

version = 0.1

setup(name='megrok.five',
      version=version,
      description="grok integration for Zope 2",
      long_description=open('README.txt').read(),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Philipp von Weitershausen",
      author_email="philipp@weitershausen.de",
      url="",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['megrok'],
      install_requires=['setuptools',
                        'grok'],
      )
