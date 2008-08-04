def insert(tree, region, provided):
    # look up insertion method
    try:
        insert = _map[region.mode]
    except KeyError:
        raise ValueError("Invalid mode: %s" % repr(region.mode))

    # insert provided content into nodes
    nodes = tree.xpath(region.xpath)
    for node in nodes:
        insert(node, provided)

def replace(node, provided):
    """Replace node with contents.

    >>> from lxml import html
    >>> tree = html.fromstring('<div>abc</div>')
    >>> from z3c.layout.browser.insertion import replace
    >>> replace(tree, html.fromstring('<div>def</div>'))
    >>> html.tostring(tree)
    '<div>def</div>'
    
    """
    
    del node[:]

    if provided.text:
        node.text = provided.text
        
    node.extend(tuple(provided))

def prepend(node, provided):
    """Prepend contents to node.

    >>> from lxml import html
    >>> tree = html.fromstring('<div>abc<span>def</span></div>')
    >>> from z3c.layout.browser.insertion import prepend
    >>> prepend(tree, html.fromstring('<div>ghi<p>jkl</p></div>'))
    >>> html.tostring(tree)
    '<div>ghiabc<p>jkl</p><span>def</span></div>'
    
    """

    if provided.text:
        node.text = provided.text + node.text or ""

    for element in reversed(provided):
        node.insert(0, element)

def append(node, provided):
    """Append contents to node.

    >>> from lxml import html
    >>> tree = html.fromstring('<div><span>abc</span>def</div>')
    >>> from z3c.layout.browser.insertion import append
    >>> append(tree, html.fromstring('<div>ghi<p>jkl</p></div>'))
    >>> html.tostring(tree)
    '<div><span>abc</span>defghi<p>jkl</p></div>'
    
    """

    if provided.text and len(node) > 0:
        last = node[-1]
        last.tail = (last.tail or "") + provided.text
    
    for element in reversed(provided):
        node.append(element)

def before(node, provided):
    """Add contents before node.

    >>> from lxml import html
    >>> tree = html.fromstring('<div><span>abc</span>def<span>ghi</span></div>')
    >>> from z3c.layout.browser.insertion import before
    >>> before(tree.xpath('.//span')[1], html.fromstring('<div>jkl<p>mno</p>pqr</div>'))
    >>> html.tostring(tree)
    '<div><span>abc</span>defjkl<p>mno</p>pqr<span>ghi</span></div>'
    
    """

    prev = node.getprevious()
    if prev is not None and provided.text:
        prev.tail = (prev.tail or "") + provided.text

    for element in reversed(provided):
        node.addprevious(element)

def after(node, provided):
    """Add contents after node.

    >>> from lxml import html
    >>> tree = html.fromstring('<div><span>abc</span>def<span>ghi</span></div>')
    >>> from z3c.layout.browser.insertion import after
    >>> after(tree.xpath('.//span')[0], html.fromstring('<div>jkl<p>mno</p>pqr</div>'))
    >>> html.tostring(tree)
    '<div><span>abc</span>jkl<p>mno</p>pqrdef<span>ghi</span></div>'
    
    """

    for element in provided:
        node.addnext(element)

    if provided.text:
        node.tail = node.tail or "" + provided.text

_map = dict(
    replace=replace,
    prepend=prepend,
    append=append,
    before=before,
    after=after)
