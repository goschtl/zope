from zope.testbrowser.utilities import disambiguate, any, onlyOne, zeroOrOne, \
    compressText
import re

def findByLabel(label, forms, include_subcontrols=False):
    # forms are iterable of mech_forms
    matches = re.compile(r'(^|\b|\W)%s(\b|\W|$)'
                         % re.escape(compressText(label))).search
    found = []
    for f in forms:
        for control in f.controls:
            phantom = control.type in ('radio', 'checkbox')
            if not phantom:
                for l in control.get_labels():
                    if matches(l.text):
                        found.append((control, f))
                        break
            if include_subcontrols and (
                phantom or control.type=='select'):

                for i in control.items:
                    for l in i.get_labels():
                        if matches(l.text):
                            found.append((i, f))
                            found_one = True
                            break

    return found

def findByName(name, forms):
    found = []
    for f in forms:
        for control in f.controls:
            if control.name==name:
                found.append((control, f))
    return found

def getControl(forms, label=None, name=None, index=None):
    intermediate, msg = getAllControls(
        forms, label, name, include_subcontrols=True)
    return disambiguate(intermediate, msg, index)

def getAllControls(forms, label, name, include_subcontrols=False):
    onlyOne([label, name], '"label" and "name"')

    if label is not None:
        res = findByLabel(label, forms, include_subcontrols)
        msg = 'label %r' % label
    elif name is not None:
        res = findByName(name, forms)
        msg = 'name %r' % name
    return res, msg

def getForm(forms, id=None, name=None, action=None, index=None):
    zeroOrOne([id, name, action], '"id", "name", and "action"')
    if index is None and not any([id, name, action]):
        raise ValueError(
            'if no other arguments are given, index is required.')

    matching_forms = []
    for form in forms:
        if ((id is not None and form.attrs.get('id') == id)
        or (name is not None and form.name == name)
        or (action is not None and re.search(action, str(form.action)))
        or id == name == action == None):
            matching_forms.append(form)

    return disambiguate(matching_forms, '', index)
