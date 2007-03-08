# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Package z3c.pdftemplate.trml2pdf.

$Id: trmlextchart.py 2701 2005-07-04 14:25:54Z daniel.meier$
"""

import utils


from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.barcharts import HorizontalBarChart3D
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.barcharts import VerticalBarChart3D
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.spider    import SpiderChart
from reportlab.graphics.charts.doughnut  import Doughnut
from reportlab.graphics.charts.slidebox  import SlideBox

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.shapes import Group
from reportlab.graphics.shapes import String

from reportlab.graphics.widgets.markers import makeMarker

from reportlab.lib import colors



class Chart(object):

    def __init__(self, renderObj, node):
        tags = {
            'LinePlot': LinePlot,
            'Pie': Pie,
            'HorizontalBarChart': HorizontalBarChart,
            'VerticalBarChart': VerticalBarChart,
            'HorizontalBarChart3D': HorizontalBarChart3D,
            'VerticalBarChart3D': VerticalBarChart3D,
            'SpiderChart': SpiderChart,
            'Doughnut': Doughnut,
            'SlideBox': SlideBox,
            }


        for k, v in tags.items():
            if k==node.getAttribute('charttype').encode('ascii'):
                self.chart = v()

        tags = {
            'LinePlot': self._linePlot,
            'Pie': self._pie,
            'HorizontalBarChart': self._horizontalBarChart,
            'VerticalBarChart': self._verticalBarChart,
            'HorizontalBarChart3D': self._horizontalBarChart3D,
            'VerticalBarChart3D': self._verticalBarChart3D,
            'SpiderChart': self._spiderChart,
            'Doughnut': self._doughnut,
            'SlideBox': self._slideBox,
            }

        if node.hasAttribute('charttype'):
            chart = tags[node.getAttribute('charttype').encode('ascii')](node);
            args = {}
            for tag in ('dwidth','dheight','dx','dy', 'dangle', ):
                if node.hasAttribute(tag):
                    args[tag] = utils.unit_get(node.getAttribute(tag))

            d = Drawing(args['dwidth'], args['dheight'])
            g = Group(chart)
            g.translate(0,0)
            g.rotate(utils.unit_get(node.getAttribute('dangle')))
            d.add(g)

            for subnode in node.getElementsByTagName('texts'):
                for tnode in subnode.getElementsByTagName('text'):
                    tstring = String(utils.unit_get(tnode.getAttribute('x')), utils.unit_get(tnode.getAttribute('y')), tnode.getAttribute('desc').encode('ascii'))
                    for tag in ('fontSize', ):
                        if tnode.hasAttribute(tag):
                            attrvalue = utils.unit_get(tnode.getAttribute(tag))
                            setattr(tstring, tag, attrvalue)

                    for tag in ('fillColor', ):
                        if tnode.hasAttribute(tag):
                            attrvalue = eval('colors.' + tnode.getAttribute(tag).encode('ascii'))
                            setattr(tstring, tag, attrvalue)

                    for tag in ('fontName', 'textAnchor'):
                        if tnode.hasAttribute(tag):
                            attrvalue = tnode.getAttribute(tag).encode('ascii')
                            setattr(tstring, tag, attrvalue)
                    g = Group(tstring)
                    g.translate(0,0)
                    g.rotate(utils.unit_get(tnode.getAttribute('angle')))
                    d.add(g)
                    #print tnode.getAttribute('desc').encode('ascii')

            d.drawOn(renderObj.canvas, args['dx'], args['dy'], _sW=0)

    def _background(self, ref, node):
        #TODO
        #isNoneOrShape
        pass


    def _label(self, ref, node):
        for tag in ('x', 'y', 'dx','dy','angle','boxStrokeWidth', 'strokeWidth', 'fontSize', 'leading', 'width', 'maxWidth', \
                    'height', 'topPadding', 'leftPadding', 'rightPadding', 'bottomPadding'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('visible', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('fontName', 'boxAnchor', 'textAnchor'):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)

        for tag in ('boxStrokeColor', 'boxFillColor', 'fillColor', 'strokeColor'):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        for tag in ('text', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, '_'+tag, attrvalue)
                #TODO
                #setText


    def _labels(self, ref, node):
        self._label(ref,node)
        tags = {
             'label': self._label,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _lineLabels(self, ref, node):
        self._label(ref,node)
        tags = {
             'lineLabel': self._label,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _barLabels(self, ref, node):
        self._label(ref,node)
        tags = {
             'barLabel': self._label,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _line(self, ref, node):
        for tag in ('strokeWidth', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('strokeDashArray', ):
            if node.hasAttribute(tag):
                attrvalue = [node.getAttribute(tag)]
                setattr(ref, tag, attrvalue)

        for tag in ('strokeColor', ):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)


        for tag in ('symbol', ):
            if node.hasAttribute(tag):
                ref.symbol =  makeMarker(node.getAttribute(tag).encode('ascii'))
        #TODO
        #shader = AttrMapValue(None, desc='Shader Class.'),
        #filler = AttrMapValue(None, desc='Filler Class.'),


    def _lines(self, ref, node):
        self._line(ref, node)
        tags = {
             'line': self._line,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _bar(self, ref, node):
        for tag in ('strokeWidth', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('strokeColor', 'fillColor'):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)
        #TODO
        #symbol = AttrMapValue(None, desc='A widget to be used instead of a normal bar.'),


    def _bars(self, ref, node):
        self._bar(ref,node)
        tags = {
             'bar': self._bar,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _slice(self, ref, node):
        for tag in ('strokeWidth', 'popout', 'fontSize', 'labelRadius', 'label_dx', 'label_dy', 'label_angle', 'label_boxStrokeWidth', \
                    'label_strokeWidth', 'label_leading', 'label_width', 'label_maxWidth', 'label_height', 'label_topPadding', \
                    'label_leftPadding', 'label_rightPadding', 'label_bottomPadding', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('fillColor', 'strokeColor', 'fontColor', 'label_boxStrokeColor', 'label_boxFillColor', 'label_strokeColor', ):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        for tag in ('fontName', 'label_text', 'label_boxAnchor', 'label_textAnchor', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)

        for tag in ('strokeDashArray', ):
            if node.hasAttribute(tag):
                attrvalue = [node.getAttribute(tag)]
                setattr(ref, tag, attrvalue)

        for tag in ('label_visible', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)


    def _slices(self, ref, node):
        self._slice(ref,node)
        tags = {
             'slice': self._slice,
            }
        i=0
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(ref[i], subnode)
                i=i+1


    def _categoryAxis(self, ref, node):
        for tag in ('strokeWidth', 'gridStrokeWidth', 'gridStart', 'gridEnd', 'joinAxisPos'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('visible', 'visibleAxis', 'visibleTicks', 'visibleLabels', 'visibleTicks', 'visibleGrid', 'joinAxis', 'reverseDirection'):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('style', 'labelAxisMode'):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)

        for tag in ('strokeColor', 'gridStrokeColor'):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        for tag in ('strokeDashArray', 'gridStrokeDashArray', 'categoryNames'):
            if node.hasAttribute(tag):
                attrvalue = eval(node.getAttribute(tag).encode('ascii'))
                #attrvalue =  node.getAttribute(tag).encode('ascii').split(",")
                setattr(ref, tag, attrvalue)

        tags = {
             'labels': self._labels,
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(ref, k), subnode)


    def _xCategoryAxis(self, ref, node):
        self._categoryAxis(ref, node)

        for tag in ('tickUp', 'tickDown'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxisMode', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


    def _yCategoryAxis(self, ref, node):
        self._categoryAxis(ref, node)

        for tag in ('tickLeft', 'tickRight', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxisMode', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


    def _valueAxis(self, ref, node):
        for tag in ('strokeWidth', 'gridStrokeWidth', 'gridStart', 'gridEnd', 'minimumTickSpacing', 'maximumTicks',\
                    'labelTextScale', 'valueMin', 'valueMax', 'valueStep', 'zrangePref' ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('forceZero', 'visible', 'visibleAxis', 'visibleLabels', 'visibleTicks', 'visibleGrid', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('labelTextFormat', 'labelTextPostFormat', 'rangeRound', 'style', 'valueSteps'):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


        for tag in ('strokeDashArray', 'gridStrokeDashArray'):
            if node.hasAttribute(tag):
                attrvalue = eval(node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        for tag in ('strokeColor', 'gridStrokeColor'):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        tags = {
             'labels': self._labels,
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(ref, k), subnode)
        #TODO
        #avoidBoundFrac = AttrMapValue(EitherOr((isNumberOrNone,SequenceOf(isNumber,emptyOK=0,lo=2,hi=2))), desc='Fraction of interval to allow above and below.'),


    def _xValueAxis(self, ref, node):
        self._valueAxis(ref, node)

        for tag in ('tickUp', 'tickDown', 'joinAxisPos'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxis', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxisMode', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


    def _normalDateXValueAxis(self, ref, node):
        for tag in ('bottomAxisLabelSlack', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('niceMonth','forceEndDate','forceFirstDate','dailyFreq'):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('xLabelFormat', 'dayOfWeekName', 'monthName'):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


    def _yValueAxis(self, ref, node):
        self._valueAxis(ref, node)

        for tag in ('tickLeft', 'tickRight', 'joinAxisPos'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxis', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('joinAxisMode', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(ref, tag, attrvalue)


    def _adjYValueAxis(self, ref, node):
        self._yValueAxis(node)

        for tag in ('requiredRange', 'leftAxisOrigShiftIPC', 'leftAxisOrigShiftMin'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('leftAxisPercent', 'leftAxisSkipLL0'):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)


    def _data(self, ref, node):
        self.chart.data=eval(node.getAttribute('dataset').encode('ascii'))


    def _annotations(self, ref, node):
        pass


    def _plotArea(self, ref, node):
        for tag in ('x', 'y', 'width', 'height', 'debug'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)

        for tag in ('strokeColor', 'strokeWidth', 'fillColor'):
            if node.hasAttribute(tag):
                attrvalue = eval('colors.' + node.getAttribute(tag).encode('ascii'))
                setattr(ref, tag, attrvalue)

        tags = {
             'background': self._background,
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(ref, k), subnode)


    def _linePlot(self, node):
        self._plotArea(self.chart, node)

        for tag in ('lineLabelNudge', 'joinedLines'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(self.chart, tag, attrvalue)

        for tag in ('reversePlotOrder', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(self.chart, tag, attrvalue)

        for tag in ('lineLabelFormat', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(self.chart, tag, attrvalue)

        tags = {
            'data': self._data,
            'lineLabels': self._lineLabels,
            'lines': self._lines,
            'xValueAxis': self._xValueAxis,
            'yValueAxis': self._yValueAxis,
            'annotations': self._annotations
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(self.chart, k), subnode)

        return self.chart


    def _pie(self, node):
        for tag in ('x', 'y', 'width', 'height', 'startangle', 'other_threshold', ):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(self.chart,tag,attrvalue)


        for tag in ('direction', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(self.chart, tag, attrvalue)

        for tag in ('simpleLabels', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(ref,tag,attrvalue)


        for tag in ('labels', ):
            if node.hasAttribute(tag):
                attrvalue =  node.getAttribute(tag).encode('ascii').split(",")
                setattr(ref, tag, attrvalue)

        tags = {
            'data': self._data,
            'slices': self._slices
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(self.chart, k), subnode)

        return self.chart


    def _barChart(self, ref, node):
        self._plotArea(self.chart, node)

        for tag in ('useAbsolute', 'barWidth', 'groupSpacing', 'barSpacing'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(self.chart, tag, attrvalue)

        for tag in ('reversePlotOrder', ):
            if node.hasAttribute(tag):
                attrvalue = utils.bool_get(node.getAttribute(tag))
                setattr(self.chart, tag, attrvalue)

        for tag in ('barLabelFormat', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii')
                setattr(self.chart, tag, attrvalue)

        for tag in ('barLabelArray', ):
            if node.hasAttribute(tag):
                attrvalue = node.getAttribute(tag).encode('ascii').split(",")
                setattr(ref, tag, attrvalue)

        tags = {
             'barLabels': self._barLabels,
             'bars': self._bars,
             'data': self._data,
             'annotations': self._annotations
            }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(self.chart, k), subnode)

    def _horizontalBarChart(self, node):
        self._barChart(self.chart, node)
        tags = {
             'valueAxis': self._xValueAxis,
             'categoryAxis': self._yCategoryAxis
             }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(self.chart, k), subnode)
        return self.chart


    def _verticalBarChart(self, node):
        self._barChart(self.chart, node)
        tags = {
             'valueAxis': self._yValueAxis,
             'categoryAxis': self._xCategoryAxis
             }
        for k, v in tags.items():
            for subnode in node.getElementsByTagName(k):
                v(getattr(self.chart, k), subnode)

        return self.chart


    def _barChart3D(self, node):
        for tag in ('theta_x', 'theta_y', 'zDepth', 'zSpace'):
            if node.hasAttribute(tag):
                attrvalue = utils.unit_get(node.getAttribute(tag))
                setattr(self.chart, tag, attrvalue)


    def _horizontalBarChart3D(self, node):
        self._verticalBarChart(node)
        self._barChart3D(node)

        return self.chart


    def _verticalBarChart3D(self, node):
        self._horizontalBarChart(node)
        self._barChart3D(node)

        return self.chart


    def _spiderChart(self, node):
        #TODO
        return self.chart


    def _doughnut(self, node):
        #TODO
        return self.chart


    def _slideBox(self, node):
        #TODO
        return self.chart

