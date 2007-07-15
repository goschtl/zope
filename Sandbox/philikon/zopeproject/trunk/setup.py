from setuptools import setup, find_packages

setup(
    name='zopeproject',
    version='0.3.1',
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    url='http://cheeseshop.python.org/pypi/zopeproject',
    download_url='svn://svn.zope.org/repos/main/Sandbox/zopeproject/trunk#egg=zopeproject-dev',
    description='Machinery and scripts for setting up new Zope projects',
    long_description=open('README.txt').read(),
    license='ZPL',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.3',],
    entry_points="""
    [console_scripts]
    zopeproject = zopeproject.main:zopeproject
    [paste.paster_create_template]
    zope_deploy = zopeproject.templates:ZopeDeploy
    zope_app = zopeproject.templates:ZopeApp
    """,
)
