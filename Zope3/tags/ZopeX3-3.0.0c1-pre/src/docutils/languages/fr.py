# Author: Stefane Fermigier
# Contact: sf@fermigier.com
# Revision: $Revision: 1.1 $
# Date: $Date: 2003/07/30 20:14:05 $
# Copyright: This module has been placed in the public domain.

"""
French-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'

labels = {
      u'author': u'Auteur',
      u'authors': u'Auteurs',
      u'organization': u'Organisation',
      u'address': u'Adresse',
      u'contact': u'Contact',
      u'version': u'Version',
      u'revision': u'R\u00e9vision',
      u'status': u'Statut',
      u'date': u'Date',
      u'copyright': u'Copyright',
      u'dedication': u'D\u00e9dicace',
      u'abstract': u'R\u00e9sum\u00e9',
      u'attention': u'Attention!',
      u'caution': u'Avertissement!',
      u'danger': u'!DANGER!',
      u'error': u'Erreur',
      u'hint': u'Indication',
      u'important': u'Important',
      u'note': u'Note',
      u'tip': u'Astuce',
      u'warning': u'Avis',
      u'contents': u'Contenu'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      u'auteur': u'author',
      u'auteurs': u'authors',
      u'organisation': u'organization',
      u'adresse': u'address',
      u'contact': u'contact',
      u'version': u'version',
      u'r\u00e9vision': u'revision',
      u'statut': u'status',
      u'date': u'date',
      u'copyright': u'copyright',
      u'd\u00e9dicace': u'dedication',
      u'r\u00e9sum\u00e9': u'abstract'}
"""French (lowcased) to canonical name mapping for bibliographic fields."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
