from setuptools import setup, find_packages
import os

readme_filename = os.path.join('src', 'megrok', 'layout', 'README.txt')
long_description = open(readme_filename).read() + '\n\n' + \
                    open(os.path.join('docs', 'HISTORY.txt')).read()



setup(name='megrok.layout',
      version='0.7',
      description="A layout component package for zope3 and Grok.",
      long_description = long_description,
      classifiers=[
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Zope",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='grok layout zope3 pagelet theming',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.layout',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'grokcore.component',
	  'grokcore.view >= 1.9',
	  'grokcore.formlib',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
