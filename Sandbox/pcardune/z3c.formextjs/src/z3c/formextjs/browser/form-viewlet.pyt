from string import Template
r+="""
var ${formVar} = new Ext.Panel({
  renderTo: '${formId}',
  width: '500px',
  frame: true,
  layout: 'form',
  title: '${formLabel}',
  html: 'My HTML content',
});
"""

r = Template(r).substitute({
    'formId':context.form.id,
    'formLabel':context.form.label,
    'formVar':'form'+context.hash(context.form.id),
    })
