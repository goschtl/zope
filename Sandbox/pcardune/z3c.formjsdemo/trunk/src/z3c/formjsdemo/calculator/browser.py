import os.path
import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from z3c.form import form, button, field
from z3c.formui import layout
from z3c.formjs import jsbutton, jsevent, interfaces

CalculatorCSSViewlet = CSSViewlet('calculator.css')

class IGridButton(interfaces.IJSButton):
    """A button within the grid."""

class Literal(jsbutton.JSButton):
    zope.interface.implements(IGridButton)

class Operator(jsbutton.JSButton):
    zope.interface.implements(IGridButton)

class IButtons(zope.interface.Interface):
    one = Literal(title=u'1')
    two = Literal(title=u'2')
    three = Literal(title=u'3')
    add = Operator(title=u'+')

    four = Literal(title=u'4')
    five = Literal(title=u'5')
    six = Literal(title=u'6')
    subtract = Operator(title=u'-')

    seven = Literal(title=u'7')
    eight = Literal(title=u'8')
    nine = Literal(title=u'9')
    multiply = Operator(title=u'*')

    zero = Literal(title=u'0')
    decimal = Literal(title=u'.')
    equal = Operator(title=u'=')
    divide = Operator(title=u'/')

    clear = jsbutton.JSButton(title=u"C")


class GridButtonActions(button.ButtonActions):

    cols = 4

    def grid(self):
        rows = []
        current = []
        for button in self.values():
            if not IGridButton.providedBy(button.field):
                continue
            current.append(button)
            if len(current) == self.cols:
                rows.append(current)
                current = []
        if current:
            current += [None]*(self.cols-len(current))
            rows.append(current)
        return rows


class CalculatorForm(layout.FormLayoutSupport, form.Form):

    buttons = button.Buttons(IButtons)

    def updateActions(self):
        self.actions = GridButtonActions(self, self.request, self.context)
        self.actions.update()

    @jsevent.handler(Operator)
    def handleOperator(self, id):
        return '''var operator = $("#operator .value").html();
                  var newOperator = $("#%s").val();
                  var current = $("#current .value").html();
                  var stack = $("#stack .value").html();
                  if (operator == ""){
                      stack = current;
                      operator = newOperator;
                  } else if(newOperator == "="){
                      current = eval(stack+operator+current);
                      stack = "";
                      operator = "";
                  } else {
                      current = eval(stack+operator+current);
                      stack = current;
                  }
                  
                  $("#operator .value").html(operator);
                  $("#stack .value").html(stack);
                  $("#recentOperator .value").html("True");
                  $("#current .value").html(current);''' % id

    @jsevent.handler(Literal)
    def handleLiteral(self, id):
        return '''var recentOperator = $("#recentOperator .value").html();
                  var current = $("#current .value").html();
                  
                  if (recentOperator != ""){
                    current = "";
                  }
                  current = current+number;
                  $("#current .value").html(current);
                  $("#recentOperator .value").html("");
                  ''' % id

    @jsevent.handler(buttons['clear'])
    def handlerClear(self, id):
        return '''$("#stack .value").html("");
                  $("#current .value").html("");
                  $("#operator .value").html("");
                  $("#recentOperator .value").html("");'''
