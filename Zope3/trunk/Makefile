PYTHON=python2.2
TESTOPTS=

all:
	$(PYTHON) stupid_build.py -q

test: all
	$(PYTHON) test.py -v $(TESTOPTS)

run:
	$(PYTHON) z3.py

clean:
	./stupid_clean
