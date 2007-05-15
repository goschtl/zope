@echo off
set args=--directory .\jsdoc
set args=%args% --logo ..\..\jsdoc\logo.gif
set args=%args% --page-footer "<div>Copyright &copy; 2007 by Projekt01 GmbH</div>"
set args=%args% --project-name "P01, Javascript API Specification"
set args=%args% --project-summary ..\..\jsdoc\summary.html
set src=.
perl ..\..\jsdoc\source\jsdoc.pl -r %args% %src%
