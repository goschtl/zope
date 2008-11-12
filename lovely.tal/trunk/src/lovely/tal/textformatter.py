##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
import re
from zope.tales.expressions import PathExpr


class TextFormatter(PathExpr):

    def __call__(self, context):
        rendered = super(TextFormatter, self).__call__(context)
        return self._doFormat(rendered, context)

    def _doFormat(self, rendered, context):

        if rendered is None:
            return rendered

        allowAll = ('allow-all' in context.vars)

        if 'clear-html' in context.vars:
            rendered = self._clearHTML(rendered, context)

        if 'cut' in context.vars:
            rendered = self._cut(rendered, context)

        if 'replace' in context.vars:
            rendered = self._replace(rendered, context)

        if 'allow' in context.vars and not allowAll:
            rendered = self._allow(rendered, context)

        if not allowAll:
            rendered = rendered.replace('<', '&lt;')
            rendered = rendered.replace('>', '&gt;')
        rendered = rendered.replace('__LOWER__', '<')
        rendered = rendered.replace('__BIGGER__', '>')

        if 'break-string' in context.vars:
            rendered = self._breakString(rendered, context)

        if 'urlparse' in context.vars:
            rendered = self._urlparse(rendered, context)

        return rendered

    def _replace(self, rendered, context):
        replace = context.vars['replace']
        for rep in replace:
            repOrig = rep[0]
            repNew = rep[1]
            repNew = repNew.replace('<', '__LOWER__')
            repNew = repNew.replace('>', '__BIGGER__')
            rendered = rendered.replace(repOrig, repNew)
        return rendered

    def _allow(self, rendered, context):
        allow = context.vars['allow']
        for al in allow:

            # find tags with opening and closing tags like <a href="bla">foo</a>
            reg = re.compile('<%s[^>]*>' %al, re.VERBOSE)
            found = reg.findall(rendered)
            for f in found:
                f_rep = f.replace('<', '__LOWER__')
                f_rep = f_rep.replace('>', '__BIGGER__')
                rendered = rendered.replace(f, f_rep)

            reg = re.compile('</%s>' %al, re.VERBOSE)
            found = reg.findall(rendered)
            for f in found:
                f_rep = f.replace('<', '__LOWER__')
                f_rep = f_rep.replace('>', '__BIGGER__')
                rendered = rendered.replace(f, f_rep)


            #find tags with no closing tag like <input type="submit" value="bla" />
            found = reg.findall(rendered)
            for f in found:
                f_rep = f.replace('<', '__LOWER__')
                f_rep = f_rep.replace('>', '__BIGGER__')
                rendered = rendered.replace(f, f_rep)
        return rendered

    def _breakString(self, rendered, context):
        lines = []
        for line in re.split('<[b|B][r|R].?/>|\n', rendered):
            lines.append(self._breakLine(line, context))
        return '<br />'.join(lines)

    def _breakLine(self, rendered, context):
        realText = rendered
        rendered = re.sub('<.*?>', '', rendered)
        br = baseBr = context.vars['break-string']
        while (br < len(rendered)):
            start = br-baseBr
            end = br
            split = re.split('\s', rendered[start:end])
            if len(split) > 1 and not re.search('\s', rendered[end]):
                # at least one \s has been found
                rep = rendered[start:end]
                idx = rep.rfind(split[-1])
                start = idx + start
                realText = self._insert('<br />', realText, start)
                br = start + baseBr

            else:
                # no break in the last baseBr characters
                realText = self._insert('<br />', realText, br)
                #rendered = rendered[:br] + '<br />' + rendered[br:]
                br = br + baseBr

        realText = re.sub('<br />\s', '<br />', realText)
        realText = re.sub('\s<br />', '<br />', realText)
        return realText

    def _insert(self, expr, realText, position):
        tags = list(re.finditer('<.*?>', realText))
        if tags == []:
            return realText[:position] + expr + realText[position:]
        for tag in tags:
            if not position > tag.start(): # a tag is before the position
                break
            position = position + len(tag.group())

        realText = realText[:position] + expr + realText[position:]
        return realText

    def _clearHTML(self, rendered, context):
        # remove tags
        return re.sub('<.*?>', '', rendered)

    def _cut(self, rendered, context):
        cut = context.vars['cut']
        if len(rendered) <= cut:
            return rendered
        rendered = rendered[:cut]
        if 'softcut' in context.vars:
            rendered = rendered.rsplit(' ', 1)[0]
        if 'attach' in context.vars:
            rendered = self._attach(rendered, context)
        return rendered

    def _attach(self, rendered, context):
        attach = context.vars['attach']
        if attach is not None:
            return rendered + attach
        return rendered

    def _urlparse(self, rendered, context):
        #searches for urls coded with www. or http:

        vars = context.vars['urlparse']
        parameters=""

        if vars:
            for k, v in vars.items():
                parameters +='%s="%s" ' % (k, v)
        else:
            parameters ='rel="nofollow" target="_blank"'

        search = re.compile(
               '(((<a\s*href\s*=\s*")?|(\s*src\s*=\s*")?)'\
               '(http:\\/\\/|www)[-A-Za-z0-9]*\\.[-A-Za-z0-9\\.]+'\
               '(~/|/|\\./)?([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:'\
               '@&=\\?/~\\#\\%]+|\\\\ )+"?)'
                )

        results = search.findall(rendered)
        searchLink = re.compile('^(<a\s*href\s*=\s*")')


        for url in results:
            if url[1] == '':
                newurl = ' <a href="%s%s" %s>%s</a> ' % (
                        'http://', 
                        url[0].lstrip(), 
                        parameters.rstrip(), 
                        url[0].lstrip())

                if url[4] == "http://":
                    newurl = '<a href="%s" %s>%s</a>' % (
                            url[0], 
                            parameters.rstrip(), 
                            url[0])

                rendered = rendered.replace(url[0],newurl)

            if searchLink.search(url[1]) and parameters !="":
                link = '%s %s' % (url[0], parameters.rstrip())
                rendered = rendered.replace(url[0],link)

        return rendered

