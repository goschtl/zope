from setuptools import setup, find_packages


setup(name='kgs.test',
      version = '1.0dev',
      author='Grok Contributors',
      author_email='grok-dev@zope.org',
      description='Tool to create test environement for KGS.',
      long_description=open('README.txt').read(),
      keywords = "zope3 setuptools egg kgs",
      classifiers = [
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Framework :: Zope3'],
      url='',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      install_requires=[
          'setuptools',
          'zc.buildout',
          ],
      entry_points = dict(console_scripts=[
          'kgs_test = kgs_test:main',
          ]),
      include_package_data = True,
      zip_safe = True,
      )
