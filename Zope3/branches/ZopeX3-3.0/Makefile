PYTHON=python2.3
TESTFLAGS=-p -v
TESTOPTS=
SETUPFLAGS=

# XXX What should the default be?
all: inplace runners

# Build in-place
inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) build_ext -i

build:
	$(PYTHON) setup.py $(SETUPFLAGS) build

runners: bin/runzope bin/zopectl

bin/runzope: Makefile
	echo "#!/bin/sh" > bin/runzope;
	echo "exec $(PYTHON) z3.py" >> bin/runzope;
	chmod +x bin/runzope

bin/zopectl: Makefile
	echo "#!/bin/sh" > bin/zopectl;
	echo "$(PYTHON) $(PWD)/src/zdaemon/zdctl.py \
	      -S schema.xml \
	      -C zdaemon.conf -d \$$*" >> bin/zopectl
	chmod +x bin/zopectl 

test_build: build
	$(PYTHON) test.py $(TESTFLAGS) $(TESTOPTS)

test_inplace: inplace
	$(PYTHON) test.py $(TESTFLAGS) $(TESTOPTS)

ftest_build: build
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

ftest_inplace: inplace
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

# XXX What should the default be?
test: test_inplace

ftest: ftest_inplace

run: inplace
	$(PYTHON) z3.py

debug: principals.zcml
	PYTHONPATH=`pwd`/src:$(PYTHONPATH) $(PYTHON) -i -c \
            "from zope.app import Application;\
             app = Application('Data.fs', 'site.zcml')()"

clean:
	find . \( -name '*.o' -o -name '*.so' -o -name '*.py[co]' -o -name '*.dll' \) -exec rm -f {} \;
	rm -rf build

realclean: clean
	rm -f TAGS
	$(PYTHON) setup.py clean -a

zcmldocs:
	PYTHONPATH=`pwd`/src:$(PYTHONPATH) $(PYTHON) \
	./src/zope/configuration/stxdocs.py \
	-f ./src/zope/app/meta.zcml -o ./doc/zcml/namespaces.zope.org


#
#   Naughty, naughty!  How many Zope3 developers are going to have
#   that directory structure?  The 'ctags' package is capable of generating
#   both emacs-sytle and vi-style tags files from python source;  can the
#   emacs-provided 'etags' not read Python?
#
TAGS:
	python ~/trunk/Tools/scripts/eptags.py `find . -name \*.py`
#	etags `find . -name \*.py -print`

tags:
	ctags -R
