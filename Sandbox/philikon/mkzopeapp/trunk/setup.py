from setuptools import setup, find_packages

setup(
    name='mkzopeapp',
    version='0.2',
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    url='http://zope.org',
    download_url='svn://svn.zope.org/repos/main/Sandbox/philikon/mkzopeapp/trunk#egg=mkzopeapp-dev',
    description='Setup script for a Zope application',
    long_description=open('README.txt').read(),
    license='ZPL',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.3',],
    entry_points="""
    [console_scripts]
    make-zope-app = mkzopeapp:make_zope_app
    deploy-zope-app = mkzopeapp:deploy_zope_app
    [paste.paster_create_template]
    make_zope_app = mkzopeapp:MakeZopeApp
    deploy_zope_app = mkzopeapp:DeployZopeApp
    """,
)
