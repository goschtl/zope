# -*- coding: utf-8 -*-
###############################################################################
#
# trml2pdf - An RML to PDF converter
# Copyright (C) 2003, Fabien Pinckaers, UCL, FSA
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################
"""Package z3c.pdftemplate.trml2pdf.

$Id: trmlextfsimage.py 2701 2005-07-04 14:25:54Z daniel.meier$
"""

import os
import utils

from reportlab.lib.utils import ImageReader 


def fsimage(self, node):
    from reportlab.lib.utils import ImageReader
    import os
    imgpath = os.path.join(os.path.dirname(__file__),str(node.getAttribute('file')))
    img = ImageReader(open(imgpath,'rb'))
    (sx,sy) = img.getSize()

    args = {}
    for tag in ('width','height','x','y'):
        if node.hasAttribute(tag):
            args[tag] = utils.unit_get(node.getAttribute(tag))
    if ('width' in args) and (not 'height' in args):
        args['height'] = sy * args['width'] / sx
    elif ('height' in args) and (not 'width' in args):
        args['width'] = sx * args['height'] / sy
    elif ('width' in args) and ('height' in args):
        if (float(args['width'])/args['height'])>(float(sx)>sy):
            args['width'] = sx * args['height'] / sy
        else:
            args['height'] = sy * args['width'] / sx
    self.canvas.drawImage(img, **args)
