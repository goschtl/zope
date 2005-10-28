#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
GUI framework and application for use with Python unit testing framework.
Execute tests written using the framework provided by the 'unittest' module.

Further information is available in the bundled documentation, and from

  http://pyunit.sourceforge.net/

Copyright (c) 1999, 2000, 2001 Steve Purcell
This module is free software, and you may redistribute it and/or modify
it under the same terms as Python itself, so long as this copyright message
and disclaimer are retained in their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__author__ = "Steve Purcell (stephen_purcell@yahoo.com)"
__version__ = "$Rev$"[6:-2]

import linecache
import unittest
import ScrolledText
import sys
import Tkinter
import tkMessageBox
import traceback

import string
import re
import os
tk = Tkinter # Alternative to the messy 'from Tkinter import *' often seen


##############################################################################
# GUI framework classes
##############################################################################

class BaseGUITestRunner:
    """Subclass this class to create a GUI TestRunner that uses a specific
    windowing toolkit. The class takes care of running tests in the correct
    manner, and making callbacks to the derived class to obtain information
    or signal that events have occurred.
    """
    def __init__(self, *args, **kwargs):
        self.currentResult = None
        self.totalTests = 0
        self.running = 0
        self.__rollbackImporter = None
        apply(self.initGUI, args, kwargs)

    def getSelectedTestName(self):
        "Override to return the name of the test selected to be run"
        pass

    def errorDialog(self, title, message):
        "Override to display an error arising from GUI usage"
        pass

    def runClicked(self, COMMA_SPACE=re.compile('[, ]+')):
        "To be called in response to user choosing to run a test"
        if self.running: return
        testName = self.getSelectedTestName()
        if not testName:
            self.errorDialog("Test name entry", "You must enter a test name")
            return
        if self.__rollbackImporter:
            self.__rollbackImporter.rollbackImports()
        self.__rollbackImporter = RollbackImporter()
        self.notifyStartImport()
        try:
            test = unittest.defaultTestLoader.loadTestsFromNames(
                COMMA_SPACE.split(testName))
            warnings = getattr(test, 'warnings', [])
            for sub_test in test._tests:
                warnings.extend(getattr(sub_test, 'warnings', []))
            test.warnings = warnings
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            apply(traceback.print_exception,sys.exc_info())
            self.errorDialog("Unable to run test '%s'" % testName,
                             "Error loading specified test: %s, %s" % \
                             (exc_type, exc_value))
            return
        self.currentResult = GUITestResult(self)
        self.totalTests = test.countTestCases()
        self.running = 1
        self.notifyRunning()
        warnings = getattr(test, 'warnings', ())
        for warning in warnings:
            self.notifyWarning(warning[0], warning[1])
        test.run(self.currentResult)
        self.running = 0
        self.notifyStopped()

    def stopClicked(self):
        "To be called in response to user stopping the running of a test"
        if self.currentResult:
            self.currentResult.stop()

    # Required callbacks

    def notifyStartImport(self):
        "Override to display a message that imports are about to start"
        pass

    def notifyRunning(self):
        "Override to set GUI in 'running' mode, enabling 'stop' button etc."
        pass

    def notifyStopped(self):
        "Override to set GUI in 'stopped' mode, enabling 'run' button etc."
        pass

    def notifyWarning(self, msg, tb_str):
        "Override to log a warning message (e.g., couldn't import a test)."

    def notifyTestFailed(self, test, err):
        "Override to indicate that a test has just failed"
        pass

    def notifyTestErrored(self, test, err):
        "Override to indicate that a test has just errored"
        pass

    def notifyTestStarted(self, test):
        "Override to indicate that a test is about to run"
        pass

    def notifyTestFinished(self, test):
        """Override to indicate that a test has finished (it may already have
           failed or errored)"""
        pass


class GUITestResult(unittest.TestResult):
    """A TestResult that makes callbacks to its associated GUI TestRunner.
    Used by BaseGUITestRunner. Need not be created directly.
    """
    def __init__(self, callback):
        unittest.TestResult.__init__(self)
        self.callback = callback

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.callback.notifyTestErrored(test, err)

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.callback.notifyTestFailed(test, err)

    def stopTest(self, test):
        unittest.TestResult.stopTest(self, test)
        self.callback.notifyTestFinished(test)

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.callback.notifyTestStarted(test)


class RollbackImporter:
    """This tricky little class is used to make sure that modules under test
    will be reloaded the next time they are imported.
    """
    def __init__(self):
        self.previousModules = sys.modules.copy()

    def rollbackImports(self):
        for modname in sys.modules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                del(sys.modules[modname])
        linecache.checkcache()


##############################################################################
# Tkinter GUI
##############################################################################

_ABOUT_TEXT="""\
PyUnit unit testing framework.

For more information, visit
http://pyunit.sourceforge.net/

Copyright (c) 2000 Steve Purcell
<stephen_purcell@yahoo.com>
"""
_HELP_TEXT="""\
Enter the name of a callable object which, when called, will return a \
TestCase or TestSuite. Click 'start', and the test thus produced will be run.

Double click on an error in the listbox to see more information about it,\
including the stack trace.

Double click on the progress bar has the same effect as clicking 'start'. \
Clicking the arrow button next to the progress bar will minimize to show \
the progress bar and arrow button *only*, making it easier to keep the \
window around during development or refactoring. Starting the GUI with the \
-m option will open the window in minimized mode by default.

For more information, visit
http://pyunit.sourceforge.net/
or see the bundled documentation
"""

class TkTestRunner(BaseGUITestRunner):
    """An implementation of BaseGUITestRunner using Tkinter.
    """
    def initGUI(self, root, initialTestName, minimal=0):
        """Set up the GUI inside the given root window. The test name entry
        field will be pre-filled with the given initialTestName.
        """
        self.root = root
        self.minimal = minimal
        # Set up values that will be tied to widgets
        self.suiteNameVar = tk.StringVar()
        self.suiteNameVar.set(initialTestName)
        self.statusVar = tk.StringVar()
        self.statusVar.set("Idle")
        self.runCountVar = tk.IntVar()
        self.failCountVar = tk.IntVar()
        self.errorCountVar = tk.IntVar()
        self.remainingCountVar = tk.IntVar()
        self.toggleVar = tk.StringVar()
        self.toggleVar.set(minimal and '>' or '<')
        self.root.withdraw()
        self.createWidgets()
        self.root.deiconify()

    def createWidgets(self):
        """Creates and packs the various widgets.

        Why is it that GUI code always ends up looking a mess, despite all the
        best intentions to keep it tidy? Answers on a postcard, please.
        """

        self.packWidgets = []
        add = self.packWidgets.append

        self.top = tk.Frame()
        add((self.top, {'fill': tk.BOTH, 'expand': 1}, 0))

        # Status bar
        statusFrame = tk.Frame(self.top, relief=tk.SUNKEN, borderwidth=2)
        add((statusFrame,
             {'anchor': tk.SW, 'fill': tk.X, 'side': tk.BOTTOM}, 1))
        add((tk.Label(statusFrame, textvariable=self.statusVar),
             {'side': tk.LEFT}, 0))

        # Area to enter name of test to run
        leftFrame = tk.Frame(self.top, borderwidth=3)
        add((leftFrame, {'fill': tk.BOTH, 'side': tk.LEFT, 'anchor': tk.NW,
                         'expand': 1}, 0))
        suiteNameFrame = tk.Frame(leftFrame, borderwidth=3)
        add((suiteNameFrame, {'fill': tk.X}, 1))
        add((tk.Label(suiteNameFrame, text="Enter test name:"),
             {'side': tk.LEFT}, 0))
        e = tk.Entry(suiteNameFrame, textvariable=self.suiteNameVar, width=80)
        add((e, {'side': tk.LEFT, 'fill': tk.X, 'expand': 1}, 0))
        e.focus_set()
        e.bind('<Key-Return>', lambda e, self=self: self.runClicked())

        # Progress bar
        progressFrame = tk.Frame(leftFrame, relief=tk.GROOVE, borderwidth=2)
        add((progressFrame, {'fill': tk.X, 'expand': 0, 'anchor': tk.NW}, 0))

        add((tk.Label(progressFrame, text="Progress:"), {'anchor': tk.W}, 1))
        tb = self.toggleButton = tk.Button(progressFrame, padx=0,
                                           relief=tk.GROOVE,
                                           textvariable=self.toggleVar,
                                           command=self.toggleMinimal)

        add((self.toggleButton, {'side': tk.LEFT, 'anchor': tk.NW}, 0))
        pb = self.progressBar = ProgressBar(progressFrame, relief=tk.SUNKEN,
                                            borderwidth=2)
        if self.minimal:
            pb.setProgressFraction(0.0, '0/0')
        add((pb, {'fill': tk.X, 'expand': 1}, 0))
        pb.bind('<Double-Button-1>', lambda e, self=self: self.runClicked())

        # Area with buttons to start/stop tests and quit
        buttonFrame = tk.Frame(self.top, borderwidth=3)
        add((buttonFrame, {'side': tk.LEFT, 'anchor': tk.NW, 'fill': tk.Y}, 1))
        self.stopGoButton = tk.Button(buttonFrame, text="Start",
                                      command=self.runClicked)
        add((self.stopGoButton, {'fill': tk.X}, 0))
        add((tk.Button(buttonFrame, text="Close", command=self.top.quit),
             {'side': tk.BOTTOM, 'fill': tk.X}, 0))
        add((tk.Button(buttonFrame, text="About", command=self.showAboutDialog),
             {'side': tk.BOTTOM, 'fill': tk.X}, 0))
        add((tk.Button(buttonFrame, text="Help", command=self.showHelpDialog),
             {'side': tk.BOTTOM, 'fill': tk.X}, 0))

        # Area with labels reporting results
        for label, var in (('Run:', self.runCountVar),
                        ('Failures:', self.failCountVar),
                        ('Errors:', self.errorCountVar),
                        ('Remaining:', self.remainingCountVar)):
            add((tk.Label(progressFrame, text=label), {'side': tk.LEFT}, 1))

            add((tk.Label(progressFrame, textvariable=var, foreground="blue"),
                 {'side': tk.LEFT, 'fill': tk.X, 'expand': 1, 'anchor': tk.W},
                 1))

        # List box showing errors and failures
        add((tk.Label(leftFrame, text="Failures and errors:"),
             {'anchor': tk.W}, 1))
        listFrame = tk.Frame(leftFrame, relief=tk.SUNKEN, borderwidth=2)
        add((listFrame, {'fill': tk.BOTH, 'anchor': tk.NW, 'expand': 1}, 1))
        self.errorListbox = tk.Listbox(listFrame, foreground='red',
                                       selectmode=tk.SINGLE,
                                       selectborderwidth=0)
        add((self.errorListbox, {'side': tk.LEFT, 'fill': tk.BOTH, 'expand': 1,
                                 'anchor': tk.NW}, 0))
        listScroll = tk.Scrollbar(listFrame, command=self.errorListbox.yview)
        add((listScroll, {'side': tk.LEFT, 'fill': tk.Y, 'anchor': tk.N}, 0))
        self.errorListbox.bind("<Double-1>",
                               lambda e, self=self: self.showSelectedError())
        self.errorListbox.configure(yscrollcommand=listScroll.set)

        # List box showing warnings

        add((tk.Label(leftFrame, text="Warnings:"), {'anchor': tk.W}, 1))
        warnFrame = tk.Frame(leftFrame, relief=tk.SUNKEN, borderwidth=2)
        add((warnFrame, {'fill': tk.BOTH, 'anchor': tk.NW, 'expand': 1}, 1))
        self.warningListbox = tk.Listbox(warnFrame, foreground='black',
                                       selectmode=tk.SINGLE,
                                       selectborderwidth=0)
        add((self.warningListbox, {'side': tk.LEFT, 'fill': tk.BOTH,
                                   'expand': 1,
                             'anchor': tk.NW}, 0))
        wListScroll = tk.Scrollbar(warnFrame, command=self.warningListbox.yview)
        add((wListScroll, {'side': tk.LEFT, 'fill': tk.Y, 'anchor': tk.N}, 0))
        self.warningListbox.bind("<Double-1>",
                               lambda e, self=self: self.showSelectedWarning())
        self.warningListbox.configure(yscrollcommand=wListScroll.set)

        # Necessary for certain X servers; X-Win32 in particular.
        self.rePack(minimal=0, with_idle_wait=1)
        self.rePack(minimal=1, with_idle_wait=1)
        self.rePack()

    def toggleMinimal(self):
        minimal = self.minimal = not self.minimal
        self.toggleVar.set(minimal and '>' or '<')
        pb = self.progressBar
        progressText = ''
        if self.minimal:
            progressText = '%d/%d' % (self.runCountVar.get(), self.totalTests)
            if self.failCountVar.get():
                progressText += ' %dF' % self.failCountVar.get()
            if self.errorCountVar.get():
                progressText += ' %dE' % self.errorCountVar.get()
            if self.warningListbox.size():
                progressText += ' %dW' % self.warningListbox.size()
        pb.setProgressFraction(pb.fraction, progressText, pb.color)
        self.rePack()

    def rePack(self, minimal=None, with_idle_wait=0):
        if minimal is None:
            minimal = self.minimal
        for widget, layoutattr, do_hide in self.packWidgets:
            if minimal and do_hide:
                widget.pack_forget()
            else:
                if not do_hide:
                    widget.pack_forget()
                apply(widget.pack, (), layoutattr)
            if with_idle_wait and not minimal:
                self.top.update_idletasks()
        self.root.geometry("")

    def getSelectedTestName(self):
        return self.suiteNameVar.get()

    def errorDialog(self, title, message):
        tkMessageBox.showerror(parent=self.root, title=title,
                               message=message)

    def notifyStartImport(self):
        if self.minimal:
            self.progressBar.setProgressFraction(0.0, 'Importing...')
        else:
            self.statusVar.set("Importing tests...")
        self.top.update_idletasks()

    def notifyRunning(self):
        self.runCountVar.set(0)
        self.failCountVar.set(0)
        self.errorCountVar.set(0)
        self.remainingCountVar.set(self.totalTests)
        self.errorInfo = []
        self.warnInfo = []
        while self.errorListbox.size():
            self.errorListbox.delete(0)
        while self.warningListbox.size():
            self.warningListbox.delete(0)
        #Stopping seems not to work, so simply disable the start button
        #self.stopGoButton.config(command=self.stopClicked, text="Stop")
        self.stopGoButton.config(state=tk.DISABLED)
        progressText = self.minimal and ('0/%d' % self.totalTests) or None
        self.progressBar.setProgressFraction(0.0, progressText)
        self.top.update_idletasks()

    def notifyStopped(self):
        self.stopGoButton.config(state=tk.ACTIVE)
        #self.stopGoButton.config(command=self.runClicked, text="Start")
        self.statusVar.set("Idle")

    def notifyTestStarted(self, test):
        test = str(test)
        if len(test) > 60:
            test = test[:30] + ' ... ' + test[-25:]
        self.statusVar.set(test)
        self.top.update_idletasks()

    def notifyWarning(self, msg, tb_str):
        self.warningListbox.insert(tk.END, "Warning: %s" % msg)
        self.warnInfo.append((msg,tb_str))

    def notifyTestFailed(self, test, err):
        self.failCountVar.set(1 + self.failCountVar.get())
        self.errorListbox.insert(tk.END, "Failure: %s" % test)
        self.errorInfo.append((test,err))

    def notifyTestErrored(self, test, err):
        self.errorCountVar.set(1 + self.errorCountVar.get())
        self.errorListbox.insert(tk.END, "Error: %s" % test)
        self.errorInfo.append((test,err))

    def notifyTestFinished(self, test):
        self.remainingCountVar.set(self.remainingCountVar.get() - 1)
        run = self.runCountVar.get() + 1
        self.runCountVar.set(run)
        fractionDone = float(run)/float(self.totalTests)
        progressText = ''
        if self.minimal:
            progressText = '%d/%d' % (run, self.totalTests)
            if self.failCountVar.get():
                progressText += ' %dF' % self.failCountVar.get()
            if self.errorCountVar.get():
                progressText += ' %dE' % self.errorCountVar.get()
            if self.warningListbox.size():
                progressText += ' %dW' % self.warningListbox.size()
        fillColor = len(self.errorInfo) and "red" or "green"
        self.progressBar.setProgressFraction(fractionDone, progressText,
            fillColor)

    def showAboutDialog(self):
        tkMessageBox.showinfo(parent=self.root, title="About PyUnit",
                              message=_ABOUT_TEXT)

    def showHelpDialog(self):
        tkMessageBox.showinfo(parent=self.root, title="PyUnit help",
                              message=_HELP_TEXT)

    def showSelectedError(self):
        selection = self.errorListbox.curselection()
        if not selection: return
        selected = int(selection[0])
        txt = self.errorListbox.get(selected)
        window = tk.Toplevel(self.root)
        window.title(txt)
        window.protocol('WM_DELETE_WINDOW', window.quit)
        test, error = self.errorInfo[selected]
        tk.Label(window, text=str(test),
                 foreground="red", justify=tk.LEFT).pack(anchor=tk.W)
        tracebackLines = apply(traceback.format_exception, error + (10,))
        tracebackText = string.join(tracebackLines,'')
        text = ScrolledText.ScrolledText(window)
        text.tag_config('sel', relief=tk.FLAT)
        text.insert(tk.END, tracebackText)
        if len(tracebackLines) < 20:
            text.config(height=len(tracebackLines) + 5)
        text.yview_pickplace(tk.END)
        text['state'] = tk.DISABLED
        text['cursor'] = window['cursor']
        self.attachEditorHotspots(text)
        text.pack(expand=1, fill=tk.BOTH)
        b = tk.Button(window, text="Close",
                      command=window.quit)
        b.pack(side=tk.BOTTOM)
        b.focus_set()
        window.bind('<Key-Return>', lambda e, w=window: w.quit())
        window.mainloop()
        window.destroy()

    def showSelectedWarning(self):
        selection = self.warningListbox.curselection()
        if not selection: return
        selected = int(selection[0])
        txt = self.warningListbox.get(selected)
        window = tk.Toplevel(self.root)
        window.title(txt)
        window.protocol('WM_DELETE_WINDOW', window.quit)
        test, error = self.warnInfo[selected]
        tk.Label(window, text=str(test),
                 foreground="black", justify=tk.LEFT).pack(anchor=tk.W)
        tk.Label(window, text=error, justify=tk.LEFT).pack()
        b = tk.Button(window, text="Close",
                      command=window.quit)
        b.pack(side=tk.BOTTOM)
        b.focus_set()
        window.bind('<Key-Return>', lambda e, w=window: w.quit())
        window.mainloop()
        window.destroy()

    def attachEditorHotspots(self, text,
            fileLine=re.compile('(File "([^"]+)", line (\d+)(?:, in \w+)?)'),
            methodLine=re.compile('^\s*(\S.*\S)\s*$')):
        # Attach clickable regions to a traceback displayed in a Text widget.
        tracebackLines = text.get('1.0', tk.END).splitlines(1)
        currentFile = ()
        tagname = ""
        start, end = 0, 0
        for i in range(len(tracebackLines)):
            match = fileLine.search(tracebackLines[i])

            # Filename, linenumber and function
            if match:
                file, line = match.group(2, 3)
                start, end = match.span(1)
                tagname = "ref%d" % i
                currentFile = (file, line, tagname)
            # Contents of that line; part of same region
            elif currentFile:
                file, line, tagname = currentFile
                start, end = methodLine.search(tracebackLines[i]).span(1)
                currentFile = ()
            # Something else
            else:
                tagname = ""

            if tagname:
                text.tag_add(tagname,
                             "%d.%d" % (i + 1, start), "%d.%d" % (i + 1, end))
                text.tag_bind(tagname, "<Enter>",
                              lambda e, n=tagname:
                                    e.widget.tag_config(n, underline=1))
                text.tag_bind(tagname, "<Leave>",
                              lambda e, n=tagname:
                                    e.widget.tag_config(n, underline=0))
                text.tag_bind(tagname, "<Button-1>",
                              lambda e, self=self, f=file, l=line:
                                    self.launchEditor(f, l))

    def launchEditor(self, file, line):
        editor = (os.environ.get('PYUNIT_EDITOR', None) or
                  os.environ.get('EDITOR_REMOTE', None) or
                  os.environ.get('EDITOR', None))
        if editor:
            os.system("%s +%s %s" % (editor, line, file))


class ProgressBar(tk.Frame):
    """A simple progress bar that shows a percentage progress in
    the given colour."""

    def __init__(self, *args, **kwargs):
        apply(tk.Frame.__init__, (self,) + args, kwargs)
        self.canvas = tk.Canvas(self, height='20', width='60',
                                background='white', borderwidth=3)
        self.canvas.pack(fill=tk.X, expand=1)
        self.rect = self.text = None
        self.canvas.bind('<Configure>', self.paint)
        self.setProgressFraction(0.0)

    def setProgressFraction(self, fraction, label='', color='blue'):
        self.fraction = fraction
        self.label = label
        self.color = color
        self.paint()
        self.canvas.update_idletasks()

    def bind(self, sequence=None, callback=None, add=None):
        "Bindings should be propagated to the contained canvas."
        tk.Frame.bind(self, sequence, callback, add)
        self.canvas.bind(sequence, callback, add)

    def unbind(self, sequence):
        "Bindings should be propagated to the contained canvas."
        tk.Frame.unbind(self, sequence)
        self.canvas.unbind(sequence)

    def bind_class(self, className, sequence=None, callback=None, add=None):
        "Bindings should be propagated to the contained canvas."
        tk.Frame.bind_class(self, className, sequence, callback, add)
        self.canvas.bind_class(className, sequence, callback, add)

    def unbind_class(self, className, sequence):
        "Bindings should be propagated to the contained canvas."
        tk.Frame.bind_class(self, className, sequence)
        self.canvas.bind_class(className, sequence)

    def paint(self, *args):
        totalWidth = self.canvas.winfo_width()
        width = int(self.fraction * float(totalWidth))
        height = self.canvas.winfo_height()
        if self.rect is not None: self.canvas.delete(self.rect)
        if self.text is not None: self.canvas.delete(self.text)
        self.rect = self.canvas.create_rectangle(0, 0, width, height,
                                                 fill=self.color)
        if self.label:
            label = self.label
        else:
            label = "%3.0f%%" % (100.0 * self.fraction)
        self.text = self.canvas.create_text(totalWidth/2, height/2,
                                            anchor=tk.CENTER,
                                            text=label)

def main(initialTestName="", minimal=0):
    root = tk.Tk()
    root.title("PyUnit")
    runner = TkTestRunner(root, initialTestName, minimal)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()


if __name__ == '__main__':
    import sys
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'm')
    minimal = ('-m', '') in opts
    if args:
        main(args[0], minimal=minimal)
    else:
        main()
