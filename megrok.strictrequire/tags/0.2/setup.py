from setuptools import setup, find_packages
import os.path

version = '0.2'
detailed = open(
    os.path.join('src', 'megrok', 'strictrequire', 'README.txt')).read()
changes = open('CHANGES.txt').read()
long_description = '\n\n'.join([detailed, changes, ''])

setup(name='megrok.strictrequire',
      version=version,
      description="Checks that all Grokked components require a permission.",
      long_description=long_description,
      classifiers=[],
      keywords=[],
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://www.thehealthagency.com',
      license='',
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          ],
      extras_require = {
          'test': ['z3c.testsetup >= 0.4',],
          },
      entry_points={},
      )
