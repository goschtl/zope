###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope.app.generations.generations import SchemaManager

pkg = 'lovely.remotetask.generations'


schemaManager = SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name=pkg)
