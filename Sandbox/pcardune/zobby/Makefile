PYTHON=python2.4
TESTFLAGS=-v
TESTOPTS=
SETUPFLAGS=
LOCALES_BASE=`pwd`/src/jsalib/locales/
DOMAINS="jsalib"
DISCARDED_ZCML="apidoc-configure.zcml \
apidoc-meta.zcml \
buddydemo-configure.zcml \
bugtracker-configure.zcml \
cache-configure.zcml \
dav-configure.zcml \
dav-meta.zcml \
debugskin-configure.zcml \
exception-ftesting.zcml \
file-configure.zcml \
ftp-configure.zcml \
helloworld-configure.zcml \
i18nfile-configure.zcml \
interpreter-configure.zcml \
preference-configure.zcml \
preference-meta.zcml \
pythonpage-configure.zcml \
rdb-configure.zcml \
rdb-meta.zcml \
renderer-meta.zcml \
schemacontent-configure.zcml \
sqlscript-configure.zcml \
testbrowser-ftesting.zcml \
tree-configure.zcml \
undo-configure.zcml \
workflow-configure.zcml \
xmlintrospection-configure.zcml \
z3checkins-configure.zcml \
zope.app.boston-configure.zcml \
zope.app.css-configure.zcml \
zope.app.demo.insensitivefolder-configure.zcml \
zope.app.demo.menu-configure.zcml \
zope.app.demo.skinpref-configure.zcml \
zope.app.demo.widget-configure.zcml \
zope.app.dtmlpage-configure.zcml \
zope.app.dtmlpage.fssync-configure.zcml \
zope.app.externaleditor-configure.zcml \
zope.app.file.fssync-configure.zcml \
zope.app.folder.fssync-configure.zcml \
zope.app.fssync-configure.zcml \
zope.app.fssync-meta.zcml \
zope.app.homefolder-configure.zcml \
zope.app.module.fssync-configure.zcml \
zope.app.pluggableauth-configure.zcml \
zope.app.recorder-configure.zcml \
zope.app.schema-configure.zcml \
zope.app.sqlexpr-configure.zcml \
zope.app.styleguide-configure.zcml \
zope.app.wfmc-configure.zcml \
zope.app.zptpage.fssync-configure.zcml \
zope.app.zptpage.textindex-configure.zcml \
zope.browsertestrecorder-configure.zcml \
zope.dublincore.fssync-configure.zcml \
zopetop-configure.zcml \
zptpage-configure.zcml \
zwiki-configure.zcml"

all: inplace

# Build in-place
inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) \
		build_ext -i install_data --install-dir Zope3
	for file in "$(DISCARDED_ZCML)"; do \
            rm -f "Zope3/zopeskel/etc/package-includes/$$file"; \
        done;

run:
	$(PYTHON) start.py

debug: principals.zcml
	PYTHONPATH=`pwd`/src:$(PYTHONPATH) $(PYTHON) -i -c \
            "from zope.app import Application;\
             app = Application('Data.fs', 'site.zcml')()"

clean:
	find . \( -name '*.o' -o -name '*.so' -o -name '*.py[co]' -o -name '*.dll' \) -exec rm -f {} \;
	rm -rf build
	rm -f Zope3/zopeskel/etc/package-includes/*.zcml
	rm -f Zope3/zopeskel/etc/securitypolicy.zcml

realclean: clean
	$(PYTHON) setup.py clean -a

.PHONY: coverage
coverage:
	rm -rf coverage
	mkdir coverage
	$(PYTHON) test.py -vp1 --coverage=coverage \
            -s z3c.form

.PHONY: coverage-report
coverage-report: coverage
	rm -rf coverage/reports
	mkdir coverage/reports
	$(PYTHON) coverage_reports.py coverage coverage/reports

i18nextract:
	PYTHONPATH=`pwd`/Zope3/src:`pwd`/src:$(PYTHONPATH) \
        $(PYTHON) i18nextract.py \
            -d z3c.form -s `pwd`/etc/site.zcml -p src -o z3c/form/locales \
	    -x zif -x zc

i18nmerge:
	PYTHONPATH=`pwd`/Zope3/src:$(PYTHONPATH) \
          $(PYTHON) Zope3/utilities/i18nmergeall.py \
          -l src/z3c/form/locales

i18nstats:
	PYTHONPATH=`pwd`/Zope3/src:$(PYTHONPATH) \
          $(PYTHON) Zope3/utilities/i18nstats.py \
          -l src/z3c/form/locales

i18ncompile:
	for domain in "$(DOMAINS)"; do \
	    msgfmt -o $(LOCALES_BASE)de/LC_MESSAGES/$$domain.mo \
	              $(LOCALES_BASE)de/LC_MESSAGES/$$domain.po; \
	done;
