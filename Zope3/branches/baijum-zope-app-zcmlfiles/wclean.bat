@rem "make clean" for Windows cmd.exe
rmdir/s/q build
del/s *.pyc *.pyo *.pyd > NUL
del zopeskel\etc\package-includes\*.zcml
del zopeskel\etc\securitypolicy.zcml
