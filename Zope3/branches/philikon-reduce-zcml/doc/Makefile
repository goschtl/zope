##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# Tell make how to convert .txt files to .html files:
.SUFFIXES: .txt .html

.txt.html::
	../utilities/rst2html $<

# Some convenient targets:
all:	toplevel schema zsync

.PHONY: toplevel
toplevel: index.html CREDITS.html DEBUG.html ENVIRONMENT.html FTEST.html \
          INSTALL.html LOGGING.html ROADMAP.html TODO.html TODOLATER.html \
          UNITTEST.html

.PHONY:	schema
schema:	schema/vocabularies.html

ZSYNC_HTML=zsync/zbundle.html zsync/zsync.html zsync/README.html
$(ZSYNC_HTML): zsync/links.rst
.PHONY:	zsync
zsync:	$(ZSYNC_HTML)
