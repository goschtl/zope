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
	$(PYTHON) test.py -v $(TESTOPTS)

test_inplace: inplace
	$(PYTHON) test.py -vB $(TESTOPTS)

# XXX What should the default be?
test: test_inplace

run:
	$(PYTHON) z3.py

clean:
	find . -name '*.o' -o -name '*.so' -o -name '*.py[co]' | xargs rm -f
	rm -f TAGS

realclean: clean
	$(PYTHON) setup.py clean -a

TAGS:
	python ~/trunk/Tools/scripts/eptags.py `find . -name \*.py`
#	etags `find . -name \*.py -print`
