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
"""ReportTool Platypus objects.
$Id$
"""
__version__='$Revision: 1.5 $'[11:-2]

import os
import string
from types import TupleType

import pprint
import imp


from reportlab.pdfgen import canvas
from reportlab.platypus import XPreformatted, Preformatted, Frame, Image
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.platypus import BaseDocTemplate, ActionFlowable, Flowable
from reportlab.platypus import PageTemplate, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import styles
from reportlab.lib import pagesizes
from reportlab.lib import colors

default_pagesize = pagesizes.A4

from Paragraph import Paragraph

## Template releated

class xmlTemplate:
    def __init__(self):
        self.filename = None
        self.pagesize = "A4"
        self.landscape = 0
        self.showboundary = 0
        self.leftmargin=10
        self.rightmargin=10
        self.topmargin=10
        self.bottommargin=10
        self.allowsplitting=1
        
        self.pagetemplates = []
        self.stylesheet = []
        
    def create(self):
        ps = getattr(pagesizes,self.pagesize,default_pagesize)
        if self.landscape:
            ps = pagesizes.landscape(ps)
            
        templates = map(lambda x,s=ps:x.create(s),self.pagetemplates)
        dt = Template(self.filename,pagesize=ps,
                 pageTemplates = templates,
                 showBoundary = self.showboundary,
                 leftMargin = self.leftmargin,
                 rightMargin = self.rightmargin,
                 topMargin = self.topmargin,
                 bottomMargin = self.bottommargin,
                 allowSplitting = self.allowsplitting)
                 
        # create StyleSheet and add custom styles
        sheet = getDefaultStyleSheet()
        if len(self.stylesheet) > 0:
            for st in self.stylesheet:
                sheet[st.name] = st.getStyle(sheet)
        dt.setStyleSheet(sheet)
        return dt
                 
        

class xmlPageTemplate:
    def __init__(self,id,nextid):
        self.id = id
        self.nextid = nextid
        self.startframe = None
        
        self.graphics = []
        self.frames = []
        
    def create(self,pagesize):
        frames = map(lambda x:x.create(),self.frames)
        pt = mPageTemplate(id=self.id,nextid=self.nextid,frames=frames,graphics=self.graphics,
                   startframe=self.startframe,pagesize=pagesize)
        return pt
        


class xmlFrame:
    def __init__(self, id, nextid, x, y, width, height):
        self.id = id
        self.nextid = nextid
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.showboundary = 0    
        self.leftpadding=10
        self.righpadding=10
        self.toppadding=10
        self.bottompadding=10

    def create(self):
        f = mFrame(self.x,self.y,self.width,self.height,
              leftPadding=self.leftpadding,
              rightPadding=self.rightpadding,
              topPadding=self.toppadding,
              bottomPadding=self.bottompadding,
              id=self.id,
              nextid=self.nextid,
              showBoundary=self.showboundary)
        return f




## Content releated (Flowables)

class xmlDocument:
    
    def __init__(self):
        self.filename = None
        self.title = None
        self.author = None
        self.subject = None
        
        self.content = []

    def create(self, template, out=None):
        template.title = self.title
        template.author = self.author
        template.subject = self.subject

        fname = out or self.filename or template.filename    
        stylesheet = template.getStyleSheet()
        return template.build(
            [fl.getFlowable(stylesheet) for fl in self.content],
            filename=fname)
        

class xmlParagraph:
    """This is a placeholder for a paragraph."""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getFlowable(self, stylesheet={}):
        p = Paragraph(
            self.rawtext,
            stylesheet[self.style],
            self.bulletText,
            context=stylesheet
            )
        return p


class xmlParagraphStyle:
    """ This is a placeholder for a paragraphstyle """
    def __init__(self,name,parent=None):
        self.name = name
        self.parent = parent
        
        self.attributes = {}        
        
    def getStyle(self,sheet={}):
        parent =  sheet.get(self.parent,None)
        p = ParagraphStyle(self.name,parent)
        for k,v in self.attributes.items():
            setattr(p,k,v)
        return p
        

class xmlPreformattedText:
    """Use this for source code, or stuff you do not want to wrap"""
    def __init__(self):
        self.rawtext = ''
        self.style = None
        self.dedent = 0

    def getFlowable(self, stylesheet={}):
        return Preformatted(self.rawtext, stylesheet[self.style],dedent=self.dedent)

class xmlXPreformattedText:
    """Use this for source code, or stuff you do not want to wrap"""
    def __init__(self):
        self.rawtext = ''
        self.style = None
        self.dedent = 0

    def getFlowable(self, stylesheet={}):
        return XPreformatted(self.rawtext, stylesheet[self.style],dedent=self.dedent)



class xmlImage:
    """Flowing image within the text"""
    def __init__(self):
        self.filename = None
        self.width = None
        self.height = None

    def getFlowable(self, stylesheet={}):
        return Image(self.filename, self.width, self.height)


class xmlTable:
    """Designed for bulk loading of data for use in presentations."""
    def __init__(self):
        self.table = None
        self.style = None  #tag args must specify
        self.rowheight = None  #tag args can override
        self.colwidth = None #tag args can override
        self.splitbyrow = 1
        self.repeatrows = 0
        self.repeatcols = 0

    def getFlowable(self, stylesheet={}):
        
        table = self.table
        
        heights = map(lambda x,y=self.rowheight: getattr(x,'rowheight',None) or y,table.rows)

        stylecmds = []
        if self.style:
            stylecmds = stylesheet[self.style].getCommands()[:]
        
        widths = []
        for c in range(0,table.colcount):
            maxwidth = self.colwidth
            for row in table.rows:
                if len(row.cells) > c:
                    maxwidth = max(maxwidth,row.cells[c].colwidth)
                        
            widths.append(maxwidth)
        
        data = []
        for row in table.rows:
            rowdata = []

            if row.stylecmd:
                stylecmds.extend(row.getStyles())

            for c in range(0,table.colcount):
                if len(row.cells) > c:
                    cell = row.cells[c]

                    if cell.stylecmd:
                        stylecmds.extend(cell.getStyles())
                    
                    content = cell.content
                    if len(content) == 1:
                        content = content[0]
                    rowdata.append(content)
                else:
                    rowdata.append(None)
            data.append(rowdata)

        t = Table(data,
              colWidths=widths,
              rowHeights=heights,
              splitByRow=self.splitbyrow,
              repeatRows=self.repeatrows,
              repeatCols=self.repeatcols)
        style = TableStyle(stylecmds)
        t.setStyle(style)
        return t


class xmlTableStyle:
    """ This is a placeholder for a tablestyle """
    def __init__(self,name):
        self.name = name
        
        self.commands = []
        
    def getStyle(self, sheet={}):
        p = TableStyle(self.commands)
        return p


class xmlSpacer:
    def __init__(self):
        self.height = 24  #points
        
    def getFlowable(self, stylesheet={}):
        return Spacer(72, self.height)

class xmlAction:
    def __init__(self):
        self.action = None
        self.params = []
        
    def getFlowable(self, stylesheet={}):
        return ActionFlowable([self.action]+self.params)


class xmlShape:

    def __init__(self):
        self.factory  = None
        self.params   = []
        self.kwparams = {}

    def getFlowable(self, stylesheet={}):
        # XXX Potential Security problem !!!!!!
        # we cannot use the mechanism from PageTemplates/PythonScripts here,
        # without making RenderPDF dependent on Zope2 :(((((
        factory = resolveFactory(self.factory)
        return apply(factory, self.params, self.kwparams)



## Static Elements

    
class xmlFixedImage:
    """You place this on the page, rather than flowing it"""
    def __init__(self):
        self.filename = None
        self.x = 0
        self.y = 0
        self.width = None
        self.height = None

    def drawOn(self, canv):
        if self.filename:
            canv.drawInlineImage(
                        self.filename,
                        self.x,
                        self.y,
                        self.width,
                        self.height
                           )


class xmlRectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.rect(self.x, self.y, self.width, self.height,
            stroke=(self.strokeColor<>None),
            fill = (self.fillColor<>None)
            )
        canv.restoreState()

                   
class xmlRoundRect:
    def __init__(self, x, y, width, height, radius):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.roundRect(self.x, self.y, self.width, self.height,
            self.radius,
            stroke=(self.strokeColor<>None),
            fill = (self.fillColor<>None)
            )
        canv.restoreState()


class xmlLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0


    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.line(self.x1, self.y1, self.x2, self.y2)
        canv.restoreState()


class xmlEllipse:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0


    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        canv.ellipse(self.x1, self.y1, self.x2, self.y2,
            stroke=(self.strokeColor<>None),
            fill = (self.fillColor<>None)
            )
        canv.restoreState()


class xmlPolygon:
    def __init__(self, pointlist):
        self.points = pointlist
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0


    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)

        path = canv.beginPath()
        (x,y) = self.points[0]
        path.moveTo(x,y)
        for (x,y) in self.points[1:]:
            path.lineTo(x,y)
        path.close()
        canv.drawPath(path, stroke=(self.strokeColor<>None))
        canv.restoreState()

    
class xmlString:
    def __init__(self, x, y):
        self.text = ''
        self.x = x
        self.y = y
        self.align = TA_LEFT
        self.font = 'Times-Roman'
        self.size = 12
        self.color = (0,0,0)
        self.hasInfo = 0  # these can have data substituted into them

    def normalizeText(self):
        """It contains literal XML text typed over several lines.
        We want to throw away
        tabs, newlines and so on, and only accept embedded string
        like '\n'"""
        lines = string.split(self.text, '\n')
        newtext = []
        for line in lines:
            newtext.append(string.strip(line))
            #accept all the '\n' as newlines

        self.text = newtext

    def drawOn(self, canv):
        # for a string in a section, this will be drawn several times;
        # so any substitution into the text should be in a temporary
        # variable
        if self.hasInfo:
            # provide a dictionary of stuff which might go into
            # the string, so they can number pages, do headers
            # etc.
            info = {}
            info['title'] = canv._doc.info.title
            info['author'] = canv._doc.info.author
            info['subject'] = canv._doc.info.subject
            info['page'] = canv.getPageNumber()
            drawText = self.text % info
        else:
            drawText = self.text

        if self.color is None:
            return
        lines = string.split(string.strip(drawText), '\\n')
        canv.saveState()
        canv.setFont(self.font, self.size)
        r,g,b = self.color
        canv.setFillColorRGB(r,g,b)
        cur_y = self.y
        for line in lines:
            if self.align == TA_LEFT:
                canv.drawString(self.x, cur_y, line)
            elif self.align == TA_CENTER:
                canv.drawCentredString(self.x, cur_y, line)
            elif self.align == TA_RIGHT:
                canv.drawRightString(self.x, cur_y, line)
            cur_y = cur_y - 1.2*self.size

        canv.restoreState()



## table helper

class xTable:
    def __init__(self,rows=[]):
        self.rows=rows
        self.rowcount=0
        self.colcount=0
        
class xRow:
    def __init__(self,cells=[]):
        self.cells=cells
        self.rowheight=0
        self.row=None
        self.stylecmd=None        
        
    def getStyles(self):
        if type(self.stylecmd) is TupleType:
            self.stylecmd = [self.stylecmd]
        cmds = []
        for sc in self.stylecmd:
            cmds.append(tuple([sc[0],(0,self.row),(-1,self.row)]+list(sc[1:])))
        return cmds
        
        
class xCell:
    def __init__(self,content=[]):
        self.content=content
        self.colwidth=0
        self.row=None
        self.col=None
        self.stylecmd=None

    def getStyles(self):
        if type(self.stylecmd) is TupleTupe:
            self.stylecmd = [self.stylecmd]
        cmds = []
        for sc in self.stylecmd:
            cmds.append(tuple([sc[0],(self.col,self.row),(self.col,self.row)]+list(sc[1:])))
        return cmds


## Layout Logic


class mFrame(Frame):
    
    def __init__(self, x1, y1, width,height, leftPadding=6, bottomPadding=6,
            rightPadding=6, topPadding=6, id=None, nextid=None, showBoundary=0):
        Frame.__init__(self,x1,y1,width,height,
              leftPadding=leftPadding,
              rightPadding=rightPadding,
              topPadding=topPadding,
              bottomPadding=bottomPadding,
              id=id,
              showBoundary=showBoundary)
        self.nextid = nextid
        self.used = 0


class mPageTemplate(PageTemplate):
    
    def __init__(self,id=None,nextid=None,frames=[],graphics=[],pagesize=default_pagesize,startframe=None):
        PageTemplate.__init__(self,id=id,frames=frames,pagesize=pagesize)
        self.nextid = nextid or self.id
        self.startframe = startframe
        self.graphics = graphics

    def beforeDrawPage(self,canv,doc):
        for graphic in self.graphics:
            graphic.drawOn(canv)




class Template(BaseDocTemplate):
    """
    """


    # Per Template Stylesheet support
    def setStyleSheet(self, stylesheet):
        self.__stylesheet = stylesheet

    def getStyleSheet(self):
        return self.__stylesheet

 
    def handle_pageBegin(self):
        self.page = self.page + 1
        self.pageTemplate.beforeDrawPage(self.canv,self)
        self.pageTemplate.checkPageSize(self.canv,self)
        self.pageTemplate.onPage(self.canv,self)
        for f in self.pageTemplate.frames: f._reset()
        self.beforePage()
        if hasattr(self,'_nextFrameIndex'):
            del self._nextFrameIndex
            
        if hasattr(self,'_linkedFrame'):
            nextframe = self._linkedFrame
            del (self._linkedFrame)
        elif self.pageTemplate.startframe is not None:
            nextframe = self.pageTemplate.startframe
        else:
            nextframe = None
            
        found = 0
        for f in self.pageTemplate.frames:
            f.used = 0
            if f.id == nextframe:
                self.frame = f
                found = 1
        if not found:
            self.frame = self.pageTemplate.frames[0]

        self._handle_nextPageTemplate(self.pageTemplate.nextid)
        
        
    def handle_frameEnd(self,resume=0):
        ''' Handles the semantics of the end of a frame. This includes the selection of
            the next frame or if this is the last frame then invoke pageEnd.
        '''
        self.frame.used = 1
        nextframe = getattr(self.frame,'nextid',None)
        
        if hasattr(self,'_nextFrameIndex'):
            self.frame = self.pageTemplate.frames[self._nextFrameIndex]
            del self._nextFrameIndex
            self.handle_frameBegin(resume)
        elif nextframe is not None:
            found = 0
            for f in self.pageTemplate.frames:
                if f.id == nextframe and not f is self.frame and not f.used==1:
                    self.frame = f
                    found = 1
            if not found:
                self._linkedFrame = nextframe
                self.handle_pageEnd()
                self.frame = None
            
        elif hasattr(self.frame,'lastFrame') or self.frame is self.pageTemplate.frames[-1]:
            self.handle_pageEnd()
            self.frame = None
        else:
            f = self.frame
            self.frame = self.pageTemplate.frames[self.pageTemplate.frames.index(f) + 1]
            self.handle_frameBegin()
         


    def build(self,flowables,filename=None, canvasmaker=canvas.Canvas):
        """Build the document from a list of flowables.
           If the filename argument is provided then that filename is used
           rather than the one provided upon initialization.
           If the canvasmaker argument is provided then it will be used
           instead of the default.      For example a slideshow might use
           an alternate canvas which places 6 slides on a page (by
           doing translations, scalings and redefining the page break
           operations).
        """
        self._calc()
        #assert filter(lambda x: not isinstance(x,Flowable), flowables)==[], "flowables argument error"
        self._startBuild(filename,canvasmaker)
 
        self.canv.setTitle(self.title or '')
        self.canv.setAuthor(self.author or 'unknown')
        self.canv.setSubject(self.subject or '')
        self.canv.setPageCompression(1)

        while len(flowables):
            self.clean_hanging()
            self.handle_flowable(flowables)
 
        self._endBuild()





## resolve Shape Factory (taken from zope3)

def resolveFactory(name, _silly=('__doc__',), _globals={}):
    name = name.strip()

    if name.endswith('.') or name.endswith('+'):
        name = name[:-1]
        repeat = 1
    else:
        repeat = 0

    names=name.split('.')
    last=names[-1]
    mod='.'.join(names[:-1])

    if not mod:
        return __import__(name, _globals, _globals, _silly)

    while 1:
        m=__import__(mod, _globals, _globals, _silly)
        try:
            a=getattr(m, last)
        except AttributeError:
            if not repeat:
                return __import__(name, _globals, _globals, _silly)

        else:
            if not repeat or (not isinstance(a, ModuleType)):
                return a
        mod += '.' + last


        
## Styles
def getDefaultStyleSheet():
    """Returns a dictionary of styles to get you started.  We will
    provide a way to specify a module of these.  Note that this
    ust includes TableStyles as well as ParagraphStyles for any
    tables you wish to use."""
    stylesheet = {}

    para = ParagraphStyle('Normal', None)   #the ancestor of all
    para.fontName = 'Helvetica'
    para.fontSize = 14
    stylesheet['Normal'] = para

    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Helvetica-Bold'
    para.fontSize = 20
    para.alignment = TA_CENTER
    stylesheet['Heading1'] = para

    para = ParagraphStyle('Cell', None)   #the ancestor of all
    para.fontName = 'Helvetica-Bold'
    para.alignment = TA_CENTER
    para.fontSize = 13
    stylesheet['Cell'] = para

    para = ParagraphStyle('CellHeading', stylesheet['Normal'])
    para.fontName = 'Helvetica-Bold'
    para.fontSize = 14
    para.alignment = TA_CENTER
    stylesheet['CellHeading'] = para

    #now for a table
    ts = TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('LINEABOVE', (0,0), (-1,0), 2, colors.black),
        ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
        ('LINEBEFORE', (-1,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),   #all numeric cells right aligned
        ('BACKGROUND', (0,0), (-1,0), colors.Color(0.8,0.8,0.8))
        ])
    stylesheet['Table'] = ts
    
    #This one is spaced out a bit...
    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 12
    stylesheet['BodyText'] = para

    #Indented, for lists
    para = ParagraphStyle('Indent', stylesheet['Normal'])
    para.leftIndent = 36
    para.firstLineIndent = 36
    stylesheet['Indent'] = para

    para = ParagraphStyle('Centered', stylesheet['Normal'])
    para.alignment = TA_CENTER
    stylesheet['Centered'] = para

    para = ParagraphStyle('BigCentered', stylesheet['Normal'])
    para.spaceBefore = 12
    para.alignment = TA_CENTER
    stylesheet['BigCentered'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Helvetica-Oblique'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Title', stylesheet['Normal'])
    para.fontName = 'Arial'
    para.fontSize = 48
    para.leading = 58
    para.alignment = TA_CENTER
    stylesheet['Title'] = para

    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Arial-Bold'
    para.fontSize = 28
    para.leading = 34
    para.spaceBefore = 24
    stylesheet['Heading2'] = para

    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Helvetica-BoldOblique'
    para.spaceBefore = 24
    stylesheet['Heading3'] = para

    para = ParagraphStyle('Heading4', stylesheet['Normal'])
    para.fontName = 'Helvetica-BoldOblique'
    para.spaceBefore = 6
    stylesheet['Heading4'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 40
    para.leftIndent = 56
    para.spaceBefore = 6
    para.bulletFontName = 'Symbol'
    para.bulletFontSize = 24
    para.bulletIndent = 20
    stylesheet['Bullet'] = para

    para = ParagraphStyle('Definition', stylesheet['Normal'])
    #use this for definition lists
    para.firstLineIndent = 72
    para.leftIndent = 72
    para.bulletIndent = 0
    para.spaceBefore = 12
    para.bulletFontName = 'Helvetica-BoldOblique'
    para.bulletFontSize = 24
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 16
    para.leading = 18
    para.leftIndent = 36
    stylesheet['Code'] = para

    para = ParagraphStyle('Small', stylesheet['Normal'])
    para.fontSize = 12
    para.leading = 14
    stylesheet['Small'] = para

    return stylesheet
