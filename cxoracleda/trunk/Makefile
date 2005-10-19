VERSION=`sed 's/\./_/g' version.txt`

clean:
	-rm `find . -type f -name "*.pyc"`
	-rm `find . -type f -name "*.~"`
	-rm `find . -type f -name semantic.cache`

cvstag:
	cvs rtag -RF v${VERSION} cxoracleda
