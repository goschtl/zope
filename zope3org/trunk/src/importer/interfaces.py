##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: $
"""

from zope.interface import Interface

class IImporter(Interface):
    """Imports a whole site into a hierachy of folders and files
    
    The files contain the whole HTML code of the pages. No post 
    processing is done at import time.
    """
    
    def download(url, base_url=None):
        """Downloads (aka imports) the site at ``url`` recursively
        
        ``url`` shall not address an index page implicitely.
        Set ``base_url`` if absolute urls in the feteched pages are 
        different than the ``url`` passed. Used if e.g. a site was 
        downloaded with wget and then parsed from the filesystem.
        """

class IPostProcessor(Interface):
    """Postprocessing HTML File(s)
    """
    
    def postprocess(site):
        """Postprocesses a file or file hierachy
        """
