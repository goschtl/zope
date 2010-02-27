from setuptools import setup, find_packages
import os

version = '0.1'

readme = open(os.join('src', 'grokcore', 'messages', 'README.txt')).read()
changes = open("CHANGES.txt").read()

setup(name='grokcore.messages',
      version=version,
      description="Grok messaging machinery",
      long_description="%s\n\n%s\n" % (readme + changes),
      keywords='Grok Messages',
      author='Souheil Chelfouh',
      author_email='souheil@chelfouh.com',
      url='',
      license='ZPL 2.1',
      namespace_packages=['grokcore'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.flashmessage',
          'grokcore.component',
      ],
      extras_require = dict(test=[
          'zope.testing',
          ]),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3',
        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
