@echo off
set PYTHON=C:\Python24\python.exe
set PYTHONPATH=.;.\src;.\Zope3;.\Zope3\src
set INSTANCE_HOME=.\src
set SOFTWARE_HOME=.\Zope3\src
"%PYTHON%" "runzodbbrowser.py"
