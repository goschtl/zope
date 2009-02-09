from setuptools import setup


setup(name='stxutils',
      version='0.1dev',
      description='StructuredText utilities',
      long_description=(open('README.txt').read() + '\n\n' +
                        open('CHANGES.txt').read()
                       ),
      packages=['stxutils'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
               'zope.structuredtext',
      ],
      entry_points = """\
        [console_scripts]
        stx2html = stxutils.tohtml:main
      """
     )
