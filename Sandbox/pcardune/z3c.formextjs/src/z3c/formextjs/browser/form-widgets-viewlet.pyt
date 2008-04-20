from string import Template

formVar = 'form%s' % context.hash(context.form.id)
for widget in context.form.widgets.values():
    w = """
    var ${widgetVar} = ${formVar}.add(new Ext.form.TextField({
      fieldLabel: '${widgetLabel}',
      value: '${widgetValue}',
      width: '300px',
      }));
    """

    r += Template(w).substitute(dict(
        widgetVar = 'widget%s' % context.hash(widget.id),
        formVar = formVar,
        widgetLabel = widget.label,
        widgetValue = escape(widget.value),
        ))

r += """
%(formVar)s.doLayout();
""" % dict(formVar=formVar)
