##
## tests.py
## Login : <uli@pu.smp.net>
## Started on  Sun Jan 20 02:54:51 2008 Uli Fouquet
## $Id$
## 
## Copyright (C) 2008 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

from zope.testing import doctest, cleanup
from zope.app.authentication.placelesssetup import PlacelessSetup

def setUp(test):
    pls = PlacelessSetup().setUp()

def tearDown(test):
    cleanup.cleanUp()

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.ELLIPSIS+
                    doctest.NORMALIZE_WHITESPACE
        )
