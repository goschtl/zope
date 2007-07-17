@echo off
set CL=/Ox
set PYTHON=C:\Python24\python.exe
set PYTHONPATH=.;..\Zope3\src;..\src;..\Zope3
set INSTANCE_HOME=..\src
set SOFTWARE_HOME=..\Zope3\src
"%PYTHON%" "setup.py%" build_ext -i install_data --install-dir .
