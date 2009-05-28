grokui.quickstart
=================

The quickstart view is registered as a default view ('index.html') for the ZODB
root folder. It is accessed from the web as http://localhost:8080/

The package registers a view for IRootFolder. This leads to a startup error if
grokui.admin <= 0.3.2 is activated, as grokui.admin also registers such a
default view.