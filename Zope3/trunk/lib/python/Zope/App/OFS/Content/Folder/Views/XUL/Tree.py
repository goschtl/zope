##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: Tree.py,v 1.2 2002/06/10 23:28:02 jim Exp $
"""


from Zope.App.PageTemplate import ViewPageTemplateFiley
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.IContainer import IReadContainer

class Tree(BrowserView):
    """ """

    def _makeSubTree(self, base, prefix=''):
        """ """
        rdf = ''
        local_links = ''
        for item in base.items():

            # first we need to create the meta data for this item
            fillIn = {'id': item[0],
                      'rdf_url': prefix + ':' + item[0]}
            rdf += _node_description %fillIn + '\n\n'

            # now we add the link to the base
            local_links += (
                '''<RDF:li resource="urn:explorer%(rdf_url)s"/>\n'''
                % fillIn)

            if IReadContainer.isImplementedBy(item[1]):
                rdf += self._makeSubTree(item[1], fillIn['rdf_url'])

        fillIn = {'links': local_links,
                  'rdf_url': prefix}
        if prefix and local_links:
            rdf += _folder_node_links %fillIn
        elif not prefix and local_links:
            rdf += _root_folder_node_links %local_links
            
        return rdf


    def getRDFTree(self, REQUEST=None):
        ''' '''
        rdf  = _rdf_start
        rdf +=  self._makeSubTree(self.context, '')
        rdf += _rdf_end
        REQUEST.response.setHeader('Content-Type', 'text/xml')
        return rdf



_rdf_start = '''<?xml version="1.0"?>

<RDF:RDF xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:explorer="http://www.zope.org/rdf#">
'''

_rdf_end = '''
</RDF:RDF>
'''

_node_description = '''
  <RDF:Description about="urn:explorer%(rdf_url)s">
    <explorer:name>%(id)s</explorer:name>
  </RDF:Description>      
'''


_folder_node_links = '''
   <RDF:Seq about="urn:explorer%(rdf_url)s">
     %(links)s
   </RDF:Seq>        
'''

_root_folder_node_links = '''
   <RDF:Seq about="urn:explorer:data">
        %s
    </RDF:Seq>                                    
'''







