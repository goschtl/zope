""" Hotfix_20060705

Disable reStructuredText's 'raw' and 'include' directives, because they allow
for information disclosuer and other nastiness.

$Id$
"""
from docutils.parsers.rst.directives import misc
del misc.raw
del misc.include;
