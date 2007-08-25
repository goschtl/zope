from setuptools import setup, find_packages

version = 0.1

setup(name='TodoList',
      version=version,
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['grok',
                        'megrok.five'],
      )
