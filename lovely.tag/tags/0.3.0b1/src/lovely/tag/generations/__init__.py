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

pkg = 'lovely.tag.generations'


schemaManager = SchemaManager(
    minimum_generation=2,
    generation=2,
    package_name=pkg)
