from setuptools import setup, find_packages

setup(
    name='ticketcollector',
    version='0.1',

    packages=find_packages('src'),
    package_dir={'': 'src'},
  
    install_requires=['setuptools',
                      'zope.app.zcmlfiles',
                      'zope.app.twisted',
                      'zope.app.securitypolicy',
                      'z3c.zrtresource',
                      ],
    include_package_data=True,
    zip_safe=False,
    )
