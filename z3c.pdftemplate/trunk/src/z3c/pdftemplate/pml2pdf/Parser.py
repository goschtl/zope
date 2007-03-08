# -*- coding: utf-8 -*-
###############################################################################
#
#   CMFReportTool - Generating PDF-Skins on the Fly from CMF-Sites
#
#   Copyright (C) 2002  net-labs Systemhaus GmbH
#                                               info@net-labs.de
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################
"""Portal forms __init__.
$Id$
"""
__version__='$Revision: 1.17 $'[11:-2]

import string
import imp

from types import ListType, DictType, UnicodeType

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import toLength
try:
    from reportlab.lib.utils import PIL_Image
except ImportError:
    PIL_Image = None

if not PIL_Image:
    try:
        # reportlab 1.19 compatibility
        from reportlab.lib.utils import Image as PIL_Image
    except ImportError:
        from PIL import Image as PIL_Image
        
import Platypus


graphic_objects = ['fixedimage', 'rectangle', 'roundrect',
                   'ellipse', 'polygon', 'line',
                   'string', 'infostring', 'customshape']

content_objects = ['para', 'prefmt', 'image', 'spacer']

alignment_enum = {'left': TA_LEFT,
                  'right':TA_RIGHT,
                  'center':TA_CENTER,
                  'justify':TA_JUSTIFY,
                  }


parameter_conversion = {'int':    string.atoi,
                        'float':  string.atof,
                        'string': str,
                        'unit':   toLength,
                        'color':  colors.toColor,
                        'alignment': alignment_enum.get,
                        }



_marker = None

def findAttrName(names, name):
    ret = None
    if name in names:
        ret = name
    lname = name.lower()
    for n,ln in [(n,n.lower()) for n in names]:
        if ln == lname:
            ret = n
            break
    return ret
    



def unescape(s):
    if '&' not in s:
        return s
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&") # Must be last
    return s



class NullResourceHandler:
    ''' basic resource Handler '''
    
    def __init__(self):
        pass
        
    def get(self,url):
        return url


class Parser:
    ''' base class'''
    
    xml_attributes = {}

    def __init__(self,dom,encoding,resourceHandler=None):
        self.dom = dom
        self.encoding = encoding
        self.resourceHandler = resourceHandler or NullResourceHandler()

    def xml_arg(self, node, name):
        if name in node.attributes.keys():
            v = node.getAttribute(name)
        else:
            if self.xml_attributes.has_key(node.nodeName):
                v = self.xml_attributes[node.nodeName][name]
            else:
                v = None
                
        if type(v) == UnicodeType:
            v = v.encode(self.encoding)
        return v

    def xml_ceval(self,node,name):
        if name in node.attributes.keys():
            v = node.getAttribute(name)
        else:
            if self.xml_attributes.has_key(node.nodeName):
                v = self.xml_attributes[node.nodeName][name]
            else:
                return None

        if type(v) == UnicodeType:
            v = v.encode(self.encoding)
        return eval(v)
        
    def xml_unit(self,node,name):
        val = self.xml_arg(node,name)
        # XXX how can val be None ??
        if val is None:
            return 0
        if val == 'None':
            return None
        return toLength(val)

    def xml_data(self,node):
        str_data = u''
        for clds in node.childNodes:
            if clds.nodeType == 3:
                str_data += clds.data
        return str_data.encode(self.encoding)

    def xml_data_list(self,node):
        list_data = []
        for clds in node.childNodes:
            if clds.nodeType == 3:
                v = clds.data
                if type(v) == UnicodeType:
                    v = v.encode(self.encoding)
                list_data.append(v)
        return list_data

    def __call__(self):
        doc = self._create()
        return doc.create()

    def _createObject(self,node):
        pass
        
    def _create(self):
        pass
            



class TemplateParser(Parser):
    ''' parses a template file'''
    
    xml_attributes = {'template': {
                'filename':'out.pdf',
                'pagesize':'A4',
                'landscape':'0',
                'showboundary':'0',
                'leftmargin':'0',  #this is ignored
                'topmargin':'0',  #this is ignored
                'rightmargin':'0',  #this is ignored
                'bottommargin':'0',  #this is ignored
                'allowsplitting':'1',
                    },
             'frame': {
                'x':'0',
                'y':'0',
                'width':'0',
                'height':'0',
                'showboundary':'0',
                'leftpadding':'0',  #this is ignored
                'toppadding':'0',  #this is ignored
                'rightpadding':'0',  #this is ignored
                'bottompadding':'0',  #this is ignored
                },
              
            'stylesheet': {
                'path':'None',
                'module':'None',
                'function':'getParagraphStyles'
                },
            'rectangle': {
                'x':'0',
                'y':'0',
                'width':'100',
                'height':'100',
                'fill':'None',
                'stroke':'(0,0,0)',
                'linewidth':'0'
                },
            'roundrect': {
                'x':'0',
                'y':'0',
                'width':'100',
                'height':'100',
                'radius':'6',
                'fill':'None',
                'stroke':'(0,0,0)',
                'linewidth':'0'

                },
            'line': {
                'x1':'0',
                'y1':'0',
                'x2':'100',
                'y2':'100',
                'stroke':'(0,0,0)',
                'width':'0'

                },
            'ellipse': {
                'x1':'0',
                'y1':'0',
                'x2':'100',
                'y2':'100',
                'stroke':'(0,0,0)',
                'fill':'None',
                'linewidth':'0'

                },
            'polygon': {
                'points':'(0,0),(50,0),(25,25)',
                'stroke':'(0,0,0)',
                'linewidth':'0',
                'stroke':'(0,0,0)',
                'fill':'None'

                },
            'string':{
                'x':'0',
                'y':'0',
                'color':'(0,0,0)',
                'font':'Times-Roman',
                'size':'12',
                'align':'left'
                },
            'infostring':{
                'x':'0',
                'y':'0',
                'color':'(0,0,0)',
                'font':'Times-Roman',
                'size':'12',
                'align':'left'
                },
            'customshape':{
                'path':'None',
                'module':'None',
                'class':'None',
                'initargs':'None'
                }
    
             }


    def _createObject(self,node):
        rhandler = self.resourceHandler
        obj = None
        if node.nodeName == 'template':
            obj = Platypus.xmlTemplate()
            obj.filename = self.xml_arg(node,'filename')
            obj.pagesize = self.xml_arg(node,'pagesize')
            obj.landscape = self.xml_ceval(node,'landscape')
            obj.showboundary = self.xml_ceval(node,'showboundary')
            obj.leftmargin = self.xml_unit(node,'leftmargin')
            obj.rightmargin = self.xml_unit(node,'rightmargin')
            obj.topmargin = self.xml_unit(node,'topmargin')
            obj.bottommargin = self.xml_unit(node,'bottommargin')
            obj.allowsplitting = self.xml_ceval(node,'allowsplitting')

        elif node.nodeName == 'pagetemplate':
            obj = Platypus.xmlPageTemplate(
                self.xml_arg(node,'id'),self.xml_arg(node,'nextid'))
            obj.startframe = self.xml_arg(node,'startframe')

        elif node.nodeName == 'frame':
            obj = Platypus.xmlFrame(
                self.xml_arg(node,'id'),
                self.xml_arg(node,'nextid'),
                self.xml_unit(node,'x'),
                self.xml_unit(node,'y'),
                self.xml_unit(node,'width'),
                self.xml_unit(node,'height')
                )
            obj.showboundary = self.xml_unit(node,'showboundary')
            obj.leftpadding = self.xml_unit(node,'leftpadding')
            obj.rightpadding = self.xml_unit(node,'rightpadding')
            obj.toppadding = self.xml_unit(node,'toppadding')
            obj.bottompadding = self.xml_unit(node,'bottompadding')

        elif node.nodeName == 'fixedimage':
            obj = Platypus.xmlFixedImage()
            obj.filename = PIL_Image.open(
                rhandler.get(self.xml_arg(node,'filename')))
            obj.x = self.xml_unit(node,'x')
            obj.y = self.xml_unit(node,'y')
            obj.width = self.xml_unit(node,'width')
            obj.height = self.xml_unit(node,'height')

        elif node.nodeName == 'rectangle':
            obj = Platypus.xmlRectangle(
                self.xml_unit(node,'x'),
                self.xml_unit(node,'y'),
                self.xml_unit(node,'width'),
                self.xml_unit(node,'height')
                )
            obj.fillColor = self.xml_ceval(node,'fill')
            obj.strokeColor = self.xml_ceval(node,'stroke')
            obj.lineWidth = self.xml_unit(node,'linewidth')

        elif node.nodeName == 'roundrect':
            obj = Platypus.xmlRoundRect(
                self.xml_unit(node,'x'),
                self.xml_unit(node,'y'),
                self.xml_unit(node,'width'),
                self.xml_unit(node,'height'),
                self.xml_unit(node,'radius')
                )
            obj.fillColor = self.xml_ceval(node,'fill')
            obj.strokeColor = self.xml_ceval(node,'stroke')
            obj.lineWidth = self.xml_unit(node,'linewidth')

        elif node.nodeName == 'line':
            obj = Platypus.xmlLine(
                self.xml_unit(node,'x1'),
                self.xml_unit(node,'y1'),
                self.xml_unit(node,'x2'),
                self.xml_unit(node,'y2')
                )
            obj.strokeColor = self.xml_ceval(node,'stroke')
            obj.lineWidth = self.xml_unit(node,'width')

        elif node.nodeName == 'ellipse':
            obj = Platypus.xmlEllipse(
                self.xml_unit(node,'x1'),
                self.xml_unit(node,'y1'),
                self.xml_unit(node,'x2'),
                self.xml_unit(node,'y2')
                )
            obj.fillColor = self.xml_ceval(node,'fill')
            obj.strokeColor = self.xml_ceval(node,'stroke')
            obj.lineWidth = self.xml_unit(node,'linewidth')

        elif node.nodeName == 'polygon':
            obj = Platypus.xmlPolygon(self.xml_ceval(node,'points'))
            obj.fillColor = self.xml_ceval(node,'fill')
            obj.strokeColor = self.xml_ceval(node,'stroke')
            obj.lineWidth = self.xml_unit(node,'linewidth')

        elif node.nodeName == 'string':
            obj = Platypus.xmlString(
                self.xml_unit(node,'x'),
                self.xml_unit(node,'y')
                )
            obj.color = self.xml_ceval(node,'color')
            obj.font = self.xml_arg(node,'font')
            obj.size = self.xml_ceval(node,'size')
            
            obj.align = alignment_enum.get(self.xml_arg(node,'align'))
            obj.text = self.xml_data(node)
            
        elif node.nodeName == 'infostring':
            obj = Platypus.xmlString(
                self.xml_unit(node,'x'),
                self.xml_unit(node,'y')
                )
            obj.color = self.xml_ceval(node,'color')
            obj.font = self.xml_arg(node,'font')
            obj.size = self.xml_ceval(node,'size')
            
            obj.align = alignment_enum.get(self.xml_arg(node,'align'))
            obj.text = self.xml_data(node)
            obj.hasInfo = 1

        elif node.nodeName == 'paragraphstyle':
            name = self.xml_arg(node, 'name')
            parent = None
            if 'parent' in node.attributes.keys():
                parent = self.xml_arg(node,'parent')
            obj = Platypus.xmlParagraphStyle(name, parent)

            names_dict = dict(
                [(n.lower(), n) for n in node.attributes.keys()])
            
            for name, conv in [
                ('fontName', self.xml_arg),
                ('fontSize', self.xml_ceval),
                ('leading', self.xml_unit),
                ('leftIndent', self.xml_unit),
                ('rightIndent', self.xml_unit),
                ('firstLineIndent', self.xml_unit),
                ('alignment',
                     lambda no, na: alignment_enum.get(self.xml_arg(no, na)) ),
                ('spaceBefore', self.xml_unit),
                ('spaceAfter', self.xml_unit),
                ('bulletFontName', self.xml_arg),
                ('bulletFontSize', self.xml_ceval),
                ('bulletIndent', self.xml_unit),
                ('textColor',
                     lambda no, na: colors.toColor(self.xml_arg(no, na)) ),
                ]:

                lowered = name.lower()
                if lowered in names_dict.keys():
                    value = conv(node, name)
                    if value is not None:
                        obj.attributes[names_dict[lowered]] = conv(node, name)

        elif node.nodeName == 'tablestyle':
            name = self.xml_arg(node,'name')
            obj = Platypus.xmlTableStyle(name)
            
        elif node.nodeName == 'stylecmd':
            obj = self.xml_ceval(node,'expr')
            
        elif node.nodeName == 'customshape':
            # XXX Potential Security problem !!!!!!
            # we cannot use the mechanism from PageTemplates/PythonScripts here,
            # without making RenderPDF dependent on Zope2 :(((((
            path = self.xml_arg(node,'path')
            if path=='None':
                path = None
            else:
                path=[path]
            modulename = self.xml_arg(node,'module')
            funcname = self.xml_arg(node,'class')
            found = imp.find_module(modulename, path)
            assert found, "CustomShape %s not found" % modulename
            (file, pathname, description) = found
            mod = imp.load_module(modulename, file, pathname, description)

            #now get the function

            func = getattr(mod, funcname)
            initargs = self.xml_ceval(node,'initargs')
            obj = apply(func, initargs)
        
        else:
            raise AttributeError, "Unknown NodeName: %s" % node.nodeName
            
        return obj
    
    def _create(self):
        
        nodesRoot = self.dom.firstChild
        current_obj = self._createObject(nodesRoot)
        obj = current_obj
        
        for nodesL1 in nodesRoot.childNodes:
            if nodesL1.nodeName == 'pagetemplate':
                current_obj = self._createObject(nodesL1)
                obj.pagetemplates.append(current_obj)
                for nodesL2 in nodesL1.childNodes:
                    if nodesL2.nodeName == 'static':
                        for nodesL3 in nodesL2.childNodes:
                            if nodesL3.nodeName in graphic_objects:
                                current_obj.graphics.append(self._createObject(nodesL3))
                    elif nodesL2.nodeName == 'frame':
                        frame = self._createObject(nodesL2)
                        current_obj.frames.append(frame)
            elif nodesL1.nodeName == 'stylesheet':
                for nodesL2 in nodesL1.childNodes:
                    if nodesL2.nodeName == 'paragraphstyle':
                        current_obj = self._createObject(nodesL2)
                        obj.stylesheet.append(current_obj)
                    elif nodesL2.nodeName == 'tablestyle':
                        current_obj = self._createObject(nodesL2)
                        for nodesL3 in nodesL2.childNodes:
                            if nodesL3.nodeName == 'stylecmd':
                                current_obj.commands.append(self._createObject(nodesL3))
                        obj.stylesheet.append(current_obj)
        return obj
            





class DocumentParser(Parser):
    ''' document parser class'''
    
    xml_attributes = {'document': {'filename':'None',
                                   },
                      'para': {'style':'Normal',
                               'bullettext':''
                               },
                      'image': {'filename':'',
                                'width':'None',
                                'height':'None'
                                },
                      'table': {'rowheight':'0',
                                'colwidth':'0',
                                'splitbyrow':'1',
                                'repeatrows':'1',
                                'repeatcols':'0',
                                'style':'None'
                                },
                      'tr' : {'rowheight':'0',
                              'stylecmd':'None',
                              },
                      'td' : {'colwidth':'0',
                              'stylecmd':'None',
                              },
                      'spacer': {'height':'24'
                                 },
                      }
             
    def _createObject(self,node):
        rhandler = self.resourceHandler
        obj = None
        if node.nodeName == 'document':
            obj = Platypus.xmlDocument()
            obj.filename = self.xml_arg(node,'filename')

        elif node.nodeName == 'para':
            obj = Platypus.xmlParagraph()
            obj.style = self.xml_arg(node,'style')
            obj.bulletText = self.xml_arg(node,'bullettext')
            text = ''
            for n in node.childNodes:
                text += n.toxml()
            if type(text) == UnicodeType:
                text = text.encode(self.encoding)
            obj.rawtext = text
        
        elif node.nodeName == 'prefmt':
            obj = Platypus.xmlPreformattedText()
            obj.style = self.xml_arg(node,'style')
            obj.dedent = int(self.xml_arg(node,'dedent') or 0)
            text = ''
            for n in node.childNodes:
                text = text + n.toxml()
            if type(text) == UnicodeType:
                text = text.encode(self.encoding)
            obj.rawtext = unescape(text)
        
        elif node.nodeName == 'xprefmt':
            obj = Platypus.xmlXPreformattedText()
            obj.style = self.xml_arg(node,'style')
            obj.dedent = int(self.xml_arg(node,'dedent') or 0)
            text = ''
            for n in node.childNodes:
                text = text + n.toxml()
            if type(text) == UnicodeType:
                text = text.encode(self.encoding)
            obj.rawtext = unescape(text)
        
        elif node.nodeName == 'image':
            obj = Platypus.xmlImage()
            obj.filename = rhandler.get(self.xml_arg(node,'filename'))
            obj.width = self.xml_unit(node,'width')
            obj.height = self.xml_unit(node,'height')
        
        elif node.nodeName == 'table':
            obj = Platypus.xmlTable()
            obj.table = Platypus.xTable()
            obj.rowheight = self.xml_unit(node,'rowheight') or None
            obj.colwidth = self.xml_unit(node,'colwidth') or None
            obj.splitbyrow = self.xml_ceval(node,'splitbyrow')
            obj.repeatrows = self.xml_ceval(node,'repeatrows')
            obj.repeatcols = self.xml_ceval(node,'repeatcols')
            if 'style' in node.attributes.keys():
                obj.style = node.getAttribute('style')

        elif node.nodeName == 'tr':
            obj = Platypus.xRow()
            obj.rowheight = self.xml_unit(node,'rowheight') or None
            if 'stylecmd' in node.attributes.keys():
                obj.stylecmd = self.xml_ceval(node,'stylecmd')

        elif node.nodeName == 'td':
            obj = Platypus.xCell()
            obj.colwidth = self.xml_unit(node,'colwidth') or None
            if 'stylecmd' in node.attributes.keys():
                obj.stylecmd = self.xml_ceval(node,'stylecmd')

        elif node.nodeName == 'spacer':
            obj = Platypus.xmlSpacer()
            obj.height = self.xml_ceval(node,'height')
            
        elif node.nodeName == 'action':
            obj = Platypus.xmlAction()
            obj.action = self.xml_arg(node,'name')
            
        elif node.nodeName == 'shape':
            obj = Platypus.xmlShape()
            obj.factory = self.xml_arg(node,'factory')
            
        elif node.nodeName == 'parameter':
            typ  = self.xml_arg(node, 'type')
            name = self.xml_arg(node, 'name')
            data = self.xml_data(node)
            if typ is not None and parameter_conversion.has_key(typ):
                data = parameter_conversion[typ](data)
                
            if name is None:
                obj = [data]
            else:
                obj = {name: data}
        
        elif node.nodeName in ['title','author','subject']:
            obj = self.xml_data(node)
        
        else:
            raise AttributeError, "Unknown NodeName: %s" % node.nodeName
            
        return obj

    
    
    
    
    def _create(self, template=None):

        stylesheet = template.getStyleSheet()
        nodesRoot = self.dom.firstChild
        current_obj = self._createObject(nodesRoot)
        obj = current_obj
        
        for nodesL1 in nodesRoot.childNodes:
            if nodesL1.nodeName == 'title':
                obj.title = self._createObject(nodesL1)
            elif nodesL1.nodeName == 'author':
                obj.author = self._createObject(nodesL1)
            elif nodesL1.nodeName == 'subject':
                obj.subject = self._createObject(nodesL1)
            elif nodesL1.nodeName == 'content':
                for nodesL2 in nodesL1.childNodes:
                    if nodesL2.nodeName in content_objects:
                        current_obj = self._createObject(nodesL2)
                        obj.content.append(current_obj)
                    elif nodesL2.nodeName == 'table':
                        current_obj = self._createObject(nodesL2)
                        rows = []
                        for nodesL3 in nodesL2.childNodes:
                            if nodesL3.nodeName == 'tr':
                                current_row = self._createObject(nodesL3)
                                current_row.row = len(rows)
                                cells = []
                                for nodesL4 in nodesL3.childNodes:
                                    if nodesL4.nodeName == 'td':
                                        current_cell = self._createObject(nodesL4)
                                        current_cell.row = current_row.row
                                        current_cell.col = len(cells)
                                        content = []
                                        str_data = u''
                                        for nodesL5 in nodesL4.childNodes:
                                            if nodesL5.nodeName == 'shape':
                                                shape_obj = self._createObject(nodesL5)
                                                params = []
                                                kwparams = {}
                                                for nodesL6 in nodesL5.childNodes:
                                                    if nodesL6.nodeName == 'parameter':
                                                        param = self._createObject(nodesL6)
                                                        param_type = type(param)
                                                        if param_type is DictType:
                                                            kwparams.update(param)
                                                        elif param_type is ListType:
                                                            params.extend(param)
                                                shape_obj.params   = params
                                                shape_obj.kwparams = kwparams
                                                content.append(shape_obj.getFlowable(stylesheet=stylesheet))
                                            
                                            elif nodesL5.nodeName in content_objects:
                                                content.append(self._createObject(nodesL5).getFlowable(stylesheet=stylesheet))
                                            elif nodesL5.nodeType == 3:
                                                str_data += nodesL5.data.strip()
                                        if content == []:
                                            if not str_data:
                                                str_data = u' '
                                            content.append(str_data.encode(self.encoding))
                                        current_cell.content = content
                                        cells.append(current_cell)

                                current_row.cells = cells
                                rows.append(current_row)
                                current_obj.table.colcount = max(current_obj.table.colcount,len(cells))
                        current_obj.table.rows = rows
                        current_obj.table.rowcount = len(rows)
                        obj.content.append(current_obj)

                    elif nodesL2.nodeName == 'action':
                        current_obj = self._createObject(nodesL2)
                        params = []
                        for nodesL3 in nodesL2.childNodes:
                            if nodesL3.nodeName == 'parameter':
                                param = self._createObject(nodesL3)
                                if type(param) is ListType:
                                    params.extend(param)
                                else:
                                    raise ValueError, 'Actions do not accept keyword parameters'
                        current_obj.params = params
                        obj.content.append(current_obj)

                    elif nodesL2.nodeName == 'shape':
                        current_obj = self._createObject(nodesL2)
                        params = []
                        kwparams = {}
                        for nodesL3 in nodesL2.childNodes:
                            if nodesL3.nodeName == 'parameter':
                                param = self._createObject(nodesL3)
                                param_type = type(param)
                                if param_type is DictType:
                                    kwparams.update(param)
                                elif param_type is ListType:
                                    params.extend(param)
                        current_obj.params   = params
                        current_obj.kwparams = kwparams
                        obj.content.append(current_obj)

        return obj
        
    def __call__(self,template,out=None):
        doc = self._create(template)
        return doc.create(template,out)
