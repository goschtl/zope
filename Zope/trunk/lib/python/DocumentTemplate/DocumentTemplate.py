##############################################################################
#
# Copyright (c) 1996-1998, Digital Creations, Fredericksburg, VA, USA.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#   o Redistributions of source code must retain the above copyright
#     notice, this list of conditions, and the disclaimer that follows.
# 
#   o Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions, and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
# 
#   o All advertising materials mentioning features or use of this
#     software must display the following acknowledgement:
# 
#       This product includes software developed by Digital Creations
#       and its contributors.
# 
#   o Neither the name of Digital Creations nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
# 
# 
# THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS AND CONTRIBUTORS *AS IS*
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL
# CREATIONS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# 
# If you have questions regarding this software, contact:
#
#   Digital Creations, L.C.
#   910 Princess Ann Street
#   Fredericksburge, Virginia  22401
#
#   info@digicool.com
#
#   (540) 371-6909
#
##############################################################################
'''Document templates with fill-in fields

Document templates provide for creation of textual documents, such as
HTML pages, from template source by inserting data from python objects
and name-spaces.

When a document template is created, a collection of default values to
be inserted may be specified with a mapping object and with keyword
arguments.

A document templated may be called to create a document with values
inserted.  When called, an instance, a mapping object, and keyword
arguments may be specified to provide values to be inserted.  If an
instance is provided, the document template will try to look up values
in the instance using getattr, so inheritence of values is supported.
If an inserted value is a function, method, or class, then an attempt
will be made to call the object to obtain values.  This allows
instance methods to be included in documents.

Document templates masquerade as functions, so the python object
publisher (Bobo) will call templates that are stored as instances of
published objects. Bobo will pass the object the template was found in
and the HTTP request object.

Two source formats are supported:

   Extended Python format strings (EPFS) --
      This format is based on the insertion by name format strings
      of python with additional format characters, '[' and ']' to
      indicate block boundaries.  In addition, parameters may be
      used within formats to control how insertion is done.

      For example:

         %%(date fmt=DayOfWeek upper)s

      causes the contents of variable 'date' to be inserted using
      custom format 'DayOfWeek' and with all lower case letters
      converted to upper case.

   HTML --
      This format uses HTML server-side-include syntax with
      commands for inserting text. Parameters may be included to
      customize the operation of a command.

      For example:

         <!--#var total fmt=12.2f-->

      is used to insert the variable 'total' with the C format
      '12.2f'.        

Document templates support conditional and sequence insertion

    Document templates extend python string substitition rules with a
    mechanism that allows conditional insertion of template text and that
    allows sequences to be inserted with element-wise insertion of
    template text.

Access Control

    Document templates provide a basic level of access control by
    preventing access to names beginning with an underscore.
    Addational control may be provided by providing document templates
    with a 'validate' method.  This would typically be done by
    subclassing one or more of the DocumentTemplate classes.

    If provided, the the 'validate' method will be called when objects
    are accessed as accessed as instance attributes or when they are
    accessed through keyed access in an expression..  The 'validate'
    method will be called with five arguments:

    1. The containing object that the object was accessed from,

    2. The actual containing object that the object was found in,
       which may be different from the containing onject the object
       was accessed from, if the containing object supports
       acquisition,

    3. The name used to acces the object,

    4. The object, and

    5. The namespace object used to render the document template.

       If a document template was called from Bobo, then the namespace
       object will have an attribute, AUTHENTICATED_USER that is the
       user object that was found if and when Bobo authenticated a user.

Document Templates may be created 4 ways:

    DocumentTemplate.String -- Creates a document templated from a
        string using an extended form of python string formatting.

    DocumentTemplate.File -- Creates a document templated bound to a
        named file using an extended form of python string formatting.
        If the object is pickled, the file name, rather than the file
        contents is pickled.  When the object is unpickled, then the
        file will be re-read to obtain the string.  Note that the file
        will not be read until the document template is used the first
        time.

    DocumentTemplate.HTML -- Creates a document templated from a
        string using HTML server-side-include rather than
        python-format-string syntax.

    DocumentTemplate.HTMLFile -- Creates an HTML document template
        from a named file.

'''


__version__='$Revision: 1.8 $'[11:-2]

ParseError='Document Template Parse Error'

from DT_String import String, File
from DT_HTML import HTML, HTMLFile, HTMLDefault
# import DT_UI # Install HTML editing
from DT_Util import html_quote
