from string import Template
# context is a widget
r += Template("""

var ${widgetVar} = ${formVar}.add(new Ext.form.TextArea({
  fieldLabel: '${widgetLabel}',
  value: '${widgetValue}',
  width: '300px',
  }));

""").substitute(dict(
    widgetVar = 'widget%s' % jsSafe(context.id),
    formVar = 'form%s' % jsSafe(context.form.id),
    widgetLabel = context.label,
    widgetValue = escape(context.value),
    ))
