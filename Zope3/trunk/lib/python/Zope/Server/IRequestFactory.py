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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

Revision information:
$Id: IRequestFactory.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface

class IRequestFactory:

    def __call__(input_stream, output_steam, environment):
        """Create a request object *with* a publication

        Factories that support multiple request/response/publication
        types may look at the environment (headers) or the stream to
        determine which request/response/publication to create.
        """



