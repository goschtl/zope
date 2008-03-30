import os
from setuptools import setup, find_packages

rules = [os.path.join('rules', f) for f in os.listdir('rules') if not f.startswith('.')]

setup(name="vanguardistas.pydebdep",
      version='0.0.3dev',
      packages=find_packages('src'),
      scripts=['pydebdep'],
      data_files=[('rules', rules)],
      namespace_packages=["vanguardistas"],
      package_dir = {'': 'src'},
      install_requires = [
          'setuptools',
          ],
      include_package_data = True,
      zip_safe = False,
      )
