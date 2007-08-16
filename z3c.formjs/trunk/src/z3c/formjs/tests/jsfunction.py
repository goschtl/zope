from z3c.formjs import jsfunction

class View(object):

    @jsfunction.pyjsfunction()
    def show(self, title):
        alert('Title' + title)
