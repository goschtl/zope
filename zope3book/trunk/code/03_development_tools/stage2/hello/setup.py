from setuptools import setup, find_packages

setup(
    name='hello',
    version='0.1',

    packages=find_packages('src'),
    package_dir={'': 'src'},
  
    install_requires=['setuptools',
                      ],
    entry_points = {'console_scripts':
                    ['print_hello = hello.say:say_hello']}, 
    include_package_data=True,
    zip_safe=False,
    )
