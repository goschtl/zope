from setuptools import setup, find_packages

version = '0.3'

setup(name='Products.ZNagios',
      version=version,
      description="ZNagios provides the ability for Nagios and munin to tap "
                  "into the Zope2 server and retrieve status and performance "
                  "data.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone i18n l10n flags',
      author="Zope Corporation and contributors",
      author_email="zope-dev@zope.org",
      url='http://pypi.python.org/pypi/Products.ZNagios',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        # 'Zope2',
      ],
)
