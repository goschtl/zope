##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# Format the documentation for the Zope Packaging Tools.

local:  $(LOCAL_HTML)
all:	local apiref


# This should point to the Zope3/utilities/rst2html, but just about
# implementation will do.
RST2HTML=rst2html

.PHONY: apiref

.SUFFIXES: .txt .html
.txt.html:
	$(RST2HTML) $<

LOCAL_HTML=\
	collections.html \
	index.html \
	metadata.html \
	resources.html \
	zpkg.html

$(LOCAL_HTML): links.rst

# Need to add dependency information for this; this really depends on
# all the modules in zpkgtools, so is tedious to spell out.
apiref: apiref/index.html
	./mkapiref.sh
