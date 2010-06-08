from setuptools import setup, find_packages
import os.path

version = '1.1'

setup(name='plone.postpublicationhook',
      version=version,
      description="Zope 2 post-publication hook",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.event',
          'zope.interface',
          'zope.security',
      ],
      extras_require={
          'Zope2.10': ['ZPublisherEventsBackport'],
      },
      )
