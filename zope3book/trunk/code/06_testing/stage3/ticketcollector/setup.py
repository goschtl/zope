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
                      ],
    extras_require=dict(test=['zope.app.testing',
                            'zope.testbrowser',
                        ]),
    include_package_data=True,
    zip_safe=False,
    )
