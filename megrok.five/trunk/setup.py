from setuptools import setup, find_packages

setup(name='megrok.five',
      version='0.1',
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      description="grok integration for Zope 2",
      download_url='svn://svn.zope.org/repos/main/megrok.five/trunk#egg=megrok.five-dev',
      long_description=open('README.txt').read(),
      license="ZPL 2.1",
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],

      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['megrok'],
      install_requires=['setuptools', 'grok'],
      )
