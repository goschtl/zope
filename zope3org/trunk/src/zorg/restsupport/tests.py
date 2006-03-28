##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
import unittest, doctest


htmlFragment = """
<p>
	This is a table
</p>
<table border="0">
	<tbody>
		<tr>
			<td>
				Cell 1
			</td>
			<td>
				Cell 2 
			</td>
		</tr>
		<tr>
			<td>
				Cell 3 
			</td>
			<td>
				Cell 4 
			</td>
		</tr>
	</tbody>
</table>
"""

htmlDocument = """<html><body>
    %s
</body>
</html>
""" % htmlFragment
    
htmlList = """
<html><body><p><i>Test</i> paragraph</p> 
    <ul>
    <li>1. Text</li>
    <li>2. Text&nbsp;</li>
    </ul>
</body></html>"""

def test_htmlTable2Rest() :
    """
    
    >>> from zorg.restsupport import html2rest
    >>> print html2rest(htmlFragment, catch_errors=False)
    Traceback (most recent call last):
    ...
    RuntimeError: cannot convert fragments
    
    
    >>> print html2rest(htmlDocument)
    This is a table
    <BLANKLINE>
    +------+------+
    |Cell 1|Cell 2|
    |      |      |
    +------+------+
    |Cell 3|Cell 4|
    |      |      |
    +------+------+
    <BLANKLINE>


    """
    
def test_htmlList2Rest() :
    """
    
    >>> from zorg.restsupport import html2rest
    >>> print html2rest(htmlList, catch_errors=False)
    *Test* paragraph
    <BLANKLINE>
    * 1. Text
    <BLANKLINE>
    * 2. Text 
    <BLANKLINE>


    """
    

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
                                    
        doctest.DocTestSuite("zorg.restsupport", 
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
