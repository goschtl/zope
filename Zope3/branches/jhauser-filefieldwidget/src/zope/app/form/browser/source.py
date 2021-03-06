##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Source widgets support

$Id$
"""
import cgi
import zope.schema.interfaces
from zope.schema.interfaces import ISourceQueriables, ValidationError
from zope.app import zapi 
import zope.app.form.interfaces
import zope.app.form.browser.widget
import zope.app.form.browser.interfaces
from zope.app.i18n import ZopeMessageIDFactory as _


class SourceDisplayWidget(zope.app.form.Widget):

    def __init__(self, field, source, request):
        super(SourceDisplayWidget, self).__init__(field, request)
        self.source = source

    def hidden(self):
        return ''

    def error(self):
        return ''

    def __call__(self):
        """Render the current value
        """

        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
            
        if value == self.context.missing_value:
            value = self._translate(_("SourceDisplayWidget-missing",
                                      default="Nothing"))
        else:
            terms = zapi.getMultiAdapter(
                (self.source, self.request),
                zope.app.form.browser.interfaces.ITerms,
                )
                
            try:
                term = terms.getTerm(value)
            except LookupError:
                value = self._translate(_("SourceDisplayWidget-invalid",
                                          default="Invalid value"))
            else:
                value = cgi.escape(term.title)

        return value

class SourceInputWidget(zope.app.form.InputWidget):

    _error = None

    zope.interface.implements(zope.app.form.interfaces.IInputWidget)

    def __init__(self, field, source, request):
        super(SourceInputWidget, self).__init__(field, request)
        self.source = source
        self.terms = zapi.getMultiAdapter(
            (source, self.request),
            zope.app.form.browser.interfaces.ITerms,
            )

        queriables = ISourceQueriables(source, None)
        if queriables is None:
            # treat the source itself as a queriable
            queriables = ((self.name, source), )
        else:
            base = self.name+'.'
            queriables = [
                (base +
                 unicode(i).encode('base64').strip().replace('=', '_'), s)
                          for (i, s) in queriables.getQueriables()]
            
        self.queryviews = [
            (i, zapi.getMultiAdapter(
                    (s, self.request),
                    zope.app.form.browser.interfaces.ISourceQueryView,
                    )
             ) for (i, s) in queriables]
            
    def _value(self):
        if self._renderedValueSet():
            value = self._data
        else:
            for name, queryview in self.queryviews:
                if name+'.apply' in self.request:
                    token = self.request.form.get(name+'.selection')
                    if token is not None:
                        break
                else:
                    token = self.request.form.get(self.name)
                
            if token is not None:
                try:
                    value = self.terms.getValue(str(token))
                except LookupError:
                    value = self.context.missing_value
            else:
                value = self.context.missing_value

        return value
    
    def hidden(self):
        value = self._value()
        if value == self.context.missing_value:
            return '' # Nothing to hide ;)

        try:
            term = self.terms.getTerm(value)
        except LookupError:
            # A value was set, but it's not valid.  Treat
            # it as if it was missing and return nothing.
            return ''
                
        return ('<input type="hidden" name="%s" value="%s">'
                % (self.name, cgi.escape(term.token))
                )

    def error(self):
        if self._error:
            return zapi.getViewProviding(self._error, IWidgetInputErrorView,
                                         self.request).snippet()
        return ""
    
    def __call__(self):
        result = ['<div class="value">']
        value = self._value()
        field = self.context

        term = None
        if value == field.missing_value:
            result.append(u'  ' +
                          self._translate(_("SourceDisplayWidget-missing",
                                            default="Nothing"))
                          )
        else:
            try:
                term = self.terms.getTerm(value)
            except LookupError:
                result.append(u'  ' +
                              self._translate(_("SourceDisplayWidget-missing",
                                                default="Nothing Valid"))
                              )
            else:
                result.append(u'  ' + cgi.escape(term.title))
                result.append('  <input type="hidden" name="%s" value="%s">'
                              % (self.name, cgi.escape(term.token)))
        result.append('  <br>')

        result.append('  <input type="hidden" name="%s.displayed" value="y">'
                      % self.name)
        
        result.append('  <div class="queries">')
        for name, queryview in self.queryviews:
            result.append('    <div class="query">')
            result.append('      <div class="queryinput">')
            result.append(queryview.render(name+'.query'))
            result.append('      </div> <!-- queryinput -->')

            qresults = queryview.results(name+'.query')
            if qresults:
                result.append('      <div class="queryresults">\n%s' %
                              self._renderResults(qresults, name))
                result.append('      </div> <!-- queryresults -->')
            result.append('    </div> <!-- query -->')
        result.append('  </div> <!-- queries -->')
        result.append('</div> <!-- value -->')
        return '\n'.join(result)

    def _renderResults(self, results, name):
        terms = []
        for value in results:
            term = self.terms.getTerm(value)
            terms.append((term.title, term.token))
        terms.sort()
        
        return (
            '<select name="%s.selection">\n'
            '%s\n'
            '</select>\n'
            '<input type="submit" name="%s.apply" value="Apply">'
            % (name,
               '\n'.join(
                   [('<option value="%s">%s</option>'
                     % (token, title))
                    for (title, token) in terms]),
               name)
            )

    required = property(lambda self: self.context.required)

    def getInputValue(self):
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                token = self.request.form.get(name+'.selection')
                if token is not None:
                    break
        else:
            token = self.request.get(self.name)

        field = self.context

        if token is None:
            if field.required:
                raise zope.app.form.interfaces.MissingInputError(
                    field.__name__, self.label,
                    )
            return field.missing_value

        try:
            value = self.terms.getValue(str(token))
        except LookupError:
            err = zope.schema.interfaces.ValidationError(
                "Invalid value id", token)
            raise WidgetInputError(field.__name__, self.label, err)

        # Remaining code copied from SimpleInputWidget

        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError, err:
            self._error = WidgetInputError(field.__name__, self.label, err)
            raise self._error

        return value

    def hasInput(self):
        if self.name in self.request:
            return True
        if (not self.context.required and
            self.name+'.displayed' in self.request):
            return True

        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                token = self.request.form.get(name+'.selection')
                if token is not None:
                    return True

        return False

class SourceListInputWidget(SourceInputWidget):

    def _input_value(self):
        tokens = self.request.form.get(self.name)
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                newtokens = self.request.form.get(name+'.selection')
                if newtokens:
                    if tokens:
                        tokens = tokens + newtokens
                    else:
                        tokens = newtokens

        if tokens:
            remove = self.request.form.get(self.name+'.checked')
            if remove and (self.name+'.remove' in self.request):
                tokens = [token
                          for token in tokens
                          if token not in remove
                          ]
            value = []
            for token in tokens:
                try:
                    v = self.terms.getValue(str(token))
                except LookupError:
                    pass # skip invalid tokens (shrug)
                else:
                    value.append(v)
        else:
            if self.name+'.displayed' in self.request:
                value = []
            else:
                value = self.context.missing_value

        if value:
            r = []
            seen = {}
            for s in value:
                if s not in seen:
                    r.append(s)
                    seen[s] = 1
            value = r

        return value

    def _value(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self._input_value()

        return value
    
    def hidden(self):
        value = self._value()
        if value == self.context.missing_value:
            return '' # Nothing to hide ;)

        result = []
        for v in value:
            try:
                term = self.terms.getTerm(value)
            except LookupError:
                # A value was set, but it's not valid.  Treat
                # it as if it was missing and skip
                continue
            else:
                result.append('<input type="hidden" name="%s:list" value="%s">'
                              % (self.name, cgi.escape(term.token))
                              )

    def __call__(self):
        result = ['<div class="value">']
        value = self._value()
        field = self.context

        if value:
            for v in value:
                try:
                    term = self.terms.getTerm(v)
                except LookupError:
                    continue # skip
                else:
                    result.append(
                        '  <input type="checkbox" name="%s.checked:list"'
                        ' value="%s">'
                        % (self.name, cgi.escape(term.token))
                        )
                    result.append('  ' + cgi.escape(term.title))
                    result.append(
                        '  <input type="hidden" name="%s:list" value="%s">'
                        % (self.name, cgi.escape(term.token)))
                    result.append('  <br>')

            result.append(
                '  <input type="submit" name="%s.remove" value="%s">'
                % (self.name,
                   self._translate(_("MultipleSourceInputWidget-remove",
                                     default="Remove")))
                )
            result.append('  <br>')

        result.append('  <input type="hidden" name="%s.displayed" value="y">'
                      % self.name)
        
        result.append('  <div class="queries">')

        for name, queryview in self.queryviews:
            result.append('    <div class="query">')
            result.append('      <div class="queryinput">')
            result.append(queryview.render(name+'.query'))
            result.append('      </div> <!-- queryinput -->')

            qresults = queryview.results(name+'.query')
            if qresults:
                result.append('      <div class="queryresults">\n%s' %
                              self._renderResults(qresults, name))
                result.append('      </div> <!-- queryresults -->')
            result.append('    </div> <!-- query -->')

        result.append('  </div> <!-- queries -->')
        result.append('</div> <!-- value -->')
        return '\n'.join(result)

    def _renderResults(self, results, name):
        terms = []
        for value in results:
            term = self.terms.getTerm(value)
            terms.append((term.title, term.token))
        terms.sort()
        return (
            '<select name="%s.selection:list" multiple>\n'
            '%s\n'
            '</select>\n'
            '<input type="submit" name="%s.apply" value="Apply">'
            % (name,
               '\n'.join([('<option value="%s">%s</option>' % (token, title))
                          for (title, token) in terms]),
               name)
            )

    def getInputValue(self):
        value = self._input_value()
            
        # Remaining code copied from SimpleInputWidget

        # value must be valid per the field constraints
        try:
            self.context.validate(value)
        except ValidationError, err:
            self._error = WidgetInputError(field.__name__, self.label, err)
            raise self._error

        return value

    def hasInput(self):
        return self.name+'.displayed' in self.request.form
