from cStringIO import StringIO
from zope import interface
from zope.testbrowser import interfaces
from zope.testbrowser.utilities import disambiguate, any, onlyOne, zeroOrOne, \
    compressText, SetattrErrorsMixin, compressText
import ClientForm
import re
import urllib2

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

def controlFactory(control, form, browser):
    if isinstance(control, ClientForm.Item):
        # it is a subcontrol
        return ItemControl(control, form, browser)
    else:
        t = control.type
        if t in ('checkbox', 'select', 'radio'):
            return ListControl(control, form, browser)
        elif t in ('submit', 'submitbutton'):
            return SubmitControl(control, form, browser)
        elif t=='image':
            return ImageControl(control, form, browser)
        else:
            return Control(control, form, browser)


class Control(SetattrErrorsMixin):
    """A control of a form."""
    interface.implements(interfaces.IControl)

    _enable_setattr_errors = False

    def __init__(self, control, form, browser):
        self.mech_control = control
        self.mech_form = form
        self.browser = browser
        self._browser_counter = self.browser._counter

        if self.mech_control.type == 'file':
            self.filename = None
            self.content_type = None

        # for some reason ClientForm thinks we shouldn't be able to modify
        # hidden fields, but while testing it is sometimes very important
        if self.mech_control.type == 'hidden':
            self.mech_control.readonly = False

        # disable addition of further attributes
        self._enable_setattr_errors = True

    @property
    def disabled(self):
        return bool(getattr(self.mech_control, 'disabled', False))

    @property
    def type(self):
        return getattr(self.mech_control, 'type', None)

    @property
    def name(self):
        return getattr(self.mech_control, 'name', None)

    @property
    def multiple(self):
        return bool(getattr(self.mech_control, 'multiple', False))

    @apply
    def value():
        """See zope.testbrowser.interfaces.IControl"""

        def fget(self):
            if (self.type == 'checkbox' and
                len(self.mech_control.items) == 1 and
                self.mech_control.items[0].name == 'on'):
                return self.mech_control.items[0].selected
            return self.mech_control.value

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            if self.mech_control.type == 'file':
                self.mech_control.add_file(value,
                                           content_type=self.content_type,
                                           filename=self.filename)
            elif self.type == 'checkbox' and len(self.mech_control.items) == 1:
                self.mech_control.items[0].selected = bool(value)
            else:
                self.mech_control.value = value
        return property(fget, fset)

    def add_file(self, file, content_type, filename):
        if not self.mech_control.type == 'file':
            raise TypeError("Can't call add_file on %s controls"
                            % self.mech_control.type)
        if isinstance(file, str):
            file = StringIO(file)
        self.mech_control.add_file(file, content_type, filename)

    def clear(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.mech_control.clear()

    def __repr__(self):
        return "<%s name=%r type=%r>" % (
            self.__class__.__name__, self.name, self.type)


class ListControl(Control):
    interface.implements(interfaces.IListControl)

    @apply
    def displayValue():
        """See zope.testbrowser.interfaces.IListControl"""
        # not implemented for anything other than select;
        # would be nice if ClientForm implemented for checkbox and radio.
        # attribute error for all others.

        def fget(self):
            return self.mech_control.get_value_by_label()

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            self.mech_control.set_value_by_label(value)

        return property(fget, fset)

    @property
    def displayOptions(self):
        """See zope.testbrowser.interfaces.IListControl"""
        res = []
        for item in self.mech_control.items:
            if not item.disabled:
                for label in item.get_labels():
                    if label.text:
                        res.append(label.text)
                        break
                else:
                    res.append(None)
        return res

    @property
    def options(self):
        """See zope.testbrowser.interfaces.IListControl"""
        if (self.type == 'checkbox' and len(self.mech_control.items) == 1 and
            self.mech_control.items[0].name == 'on'):
            return [True]
        return [i.name for i in self.mech_control.items if not i.disabled]

    @property
    def disabled(self):
        if self.type == 'checkbox' and len(self.mech_control.items) == 1:
            return bool(getattr(self.mech_control.items[0], 'disabled', False))
        return bool(getattr(self.mech_control, 'disabled', False))

    @property
    def controls(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        res = [controlFactory(i, self.mech_form, self.browser) for i in
                self.mech_control.items]
        for s in res:
            s.__dict__['control'] = self
        return res

    def getControl(self, label=None, value=None, index=None):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError

        onlyOne([label, value], '"label" and "value"')

        if label is not None:
            options = self.mech_control.get_items(label=label)
            msg = 'label %r' % label
        elif value is not None:
            options = self.mech_control.get_items(name=value)
            msg = 'value %r' % value
        res = controlFactory(
            disambiguate(options, msg, index), self.mech_form, self.browser)
        res.__dict__['control'] = self
        return res


class SubmitControl(Control):
    interface.implements(interfaces.ISubmitControl)

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._clickSubmit(self.mech_form, self.mech_control, (1,1))
        self.browser._changed()


class ImageControl(Control):
    interface.implements(interfaces.IImageSubmitControl)

    def click(self, coord=(1,1)):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._clickSubmit(self.mech_form, self.mech_control, coord)
        self.browser._changed()


class ItemControl(SetattrErrorsMixin):
    interface.implements(interfaces.IItemControl)

    def __init__(self, item, form, browser):
        self.mech_item = item
        self.mech_form = form
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def control(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        res = controlFactory(
            self.mech_item._control, self.mech_form, self.browser)
        self.__dict__['control'] = res
        return res

    @property
    def disabled(self):
        return self.mech_item.disabled

    @apply
    def selected():
        """See zope.testbrowser.interfaces.IControl"""

        def fget(self):
            return self.mech_item.selected

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            self.mech_item.selected = value

        return property(fget, fset)

    @property
    def optionValue(self):
        return self.mech_item.attrs.get('value')

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.mech_item.selected = not self.mech_item.selected

    def __repr__(self):
        return "<%s name=%r type=%r optionValue=%r>" % (
            self.__class__.__name__, self.mech_item._control.name,
            self.mech_item._control.type, self.optionValue)


class Form(SetattrErrorsMixin):
    """HTML Form"""
    interface.implements(interfaces.IForm)

    def __init__(self, browser, form):
        """Initialize the Form

        browser - a Browser instance
        form - a ClientForm instance
        """
        self.browser = browser
        self.mech_form = form
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def action(self):
        return self.mech_form.action

    @property
    def method(self):
        return self.mech_form.method

    @property
    def enctype(self):
        return self.mech_form.enctype

    @property
    def name(self):
        return self.mech_form.name

    @property
    def id(self):
        """See zope.testbrowser.interfaces.IForm"""
        return self.mech_form.attrs.get('id')

    def submit(self, label=None, name=None, index=None, coord=(1,1)):
        """See zope.testbrowser.interfaces.IForm"""
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        form = self.mech_form
        if label is not None or name is not None:
            intermediate, msg = getAllControls([form], label, name)
            intermediate = [
                (control, form) for (control, form) in intermediate if
                control.type in ('submit', 'submitbutton', 'image')]
            control, form = disambiguate(intermediate, msg, index)
            self.browser._clickSubmit(form, control, coord)
        else: # JavaScript sort of submit
            if index is not None or coord != (1,1):
                raise ValueError(
                    'May not use index or coord without a control')
            request = self.mech_form._switch_click("request", urllib2.Request)
            self.browser._start_timer()
            self.browser.mech_browser.open(request)
            self.browser._stop_timer()
        self.browser._changed()

    def getControl(self, label=None, name=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        forms = [self.mech_form]
        intermediate, msg = getAllControls(forms, label, name,
                                           include_subcontrols=True)
        control, form = disambiguate(intermediate, msg, index)
        return controlFactory(control, form, self.browser)
