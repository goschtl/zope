PYTHON=python2.2
TESTOPTS=

# XXX What should the default be?
all: inplace

# Build in-place
inplace:
	$(PYTHON) setup.py -q build_ext -i

build:
	$(PYTHON) setup.py -q build

test_build: build
	$(PYTHON) test.py -p -v $(TESTOPTS)

test_inplace: inplace
	$(PYTHON) test.py -p -v $(TESTOPTS)

# XXX What should the default be?
test: test_inplace

run:
	$(PYTHON) z3.py

clean:
	find . -name '*.o' -o -name '*.so' -o -name '*.py[co]' | xargs rm -f
	rm -rf build

realclean: clean
	rm -f TAGS
	$(PYTHON) setup.py clean -a

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
