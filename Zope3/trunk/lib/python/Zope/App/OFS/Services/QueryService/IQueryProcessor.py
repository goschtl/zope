##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: IQueryProcessor.py,v 1.1 2002/12/03 16:30:17 ctheune Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class IQueryProcessor(Interface):
    
    input_interface = Attribute("The __implements__-like specification "
                                "for the input interfaces.")
    output_interface = Attribute("The __implements__-like specification "
                                 "for the output interfaces.")

    def __call__(query):
        """Processes the query returning the result.

           The query must be adaptable to each interface in input_interface.
           The output should be adaptable to each interface in the
           output_interface.
        """
