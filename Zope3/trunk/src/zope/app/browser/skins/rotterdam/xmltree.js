//constants
var ELEMENT_NODE = 1;
var TEXT_NODE = 3;
var COLLECTION = 'COLLECTION';
var TITLE = 'TITLE';
var ICON = 'ICON';
var EXPAND = 'EXPAND';
var XML_CHILDREN_VIEW = '@@children.xml';
var SINGLE_BRANCH_TREE_VIEW = '@@singleBranchTree.xml';
var CONTENT_VIEW = '@@contents.html';


var LG_DEBUG = 6;
var LG_TRACE_EVENTS = 5;
var LG_TRACE = 4;
var LG_INFO = 3;
var LG_NOLOG = 0;


// globals
var baseurl;
var navigationTree;

var loglevel = LG_NOLOG;



//class navigationTreeNode
function navigationTreeNode (domNode) {
        this.childNodes = new Array();
        this.isEmpty = 1;
        this.isCollapsed = 1;
        this.domNode = domNode;
        this.name = '';
        this.parentNode = null;
}

navigationTreeNode.prototype.appendChild = function(node) {
        this.childNodes.push(node);
        this.domNode.appendChild(node.domNode);
        node.parentNode = this;
}

navigationTreeNode.prototype.getName = function() {
        return this.name;
}

navigationTreeNode.prototype.setName = function(name) {
        this.name = name;
        this.domNode.setAttribute("name", name);
}

navigationTreeNode.prototype.collapse = function() {
 	this.isCollapsed = 1;
        changeExpandIcon(this.domNode, "pl.gif"); 
}

navigationTreeNode.prototype.expand = function() {
 	this.isCollapsed = 0;
        changeExpandIcon(this.domNode, "mi.gif"); 
}

navigationTreeNode.prototype.getNodeByName = function(name) {
        var numchildren = this.childNodes.length;
        if (name == this.name) {
                return this;
                }
        else {
                for (var i=0; i< numchildren; i++) {
                        foundChild = this.childNodes[i].getNodeByName(name);
                        if (foundChild) {
                                return foundChild;
                                }
                        }        
                }
        return null;
}

// utilities
function prettydump(s, locallog) {
        // Put the string "s" in a box on the screen as an log message
        if (locallog <= loglevel) {
                var logger = document.getElementById('logger');
  	        var msg = document.createElement('code');
	        var br1 = document.createElement('br');
  	        var br2 = document.createElement('br');
  	        var msg_text = document.createTextNode(s);
  	        msg.appendChild(msg_text);
          	logger.insertBefore(br1, logger.firstChild);
  	        logger.insertBefore(br2, logger.firstChild);
          	logger.insertBefore(msg, logger.firstChild);
	        }
        }


function debug(s) {
        var oldlevel = loglevel;
        loglevel = LG_DEBUG;
        prettydump("Debug : " + s, LG_DEBUG);
        loglevel = oldlevel;
}

// DOM utilities
function getTreeEventTarget(e) {
	var elem;
        if(e.target) {
                // Mozilla uses this
       		if (e.target.nodeType == TEXT_NODE) {
                        elem=e.target.parentNode;
		        }
		else {
		        elem=e.target;
			}
                }
        else {
                // IE uses this
                elem=e.srcElement;
                }
        return elem;
        }

function isCollection(elem) {
	return (checkTagName(elem, COLLECTION));
	}

function isTitle(elem) {
	return (checkTagName(elem, TITLE));
	}

function isIcon(elem) {
	return (checkTagName(elem, ICON));
	}

function isExpand(elem) {
	return (checkTagName(elem, EXPAND));
	}

function checkTagName(elem, tagName) {
	return (elem.tagName.toUpperCase() == tagName);
	}

function toggleExpansion (navTreeNode) {
	prettydump('toggleExpansion', LG_TRACE);
        // If this collection is empty, load it from server
        // todo xxx optimize for the case where collection has null length
        var elem = navTreeNode.domNode;
        if (navTreeNode.isEmpty) {
                var url = baseurl + navTreeNode.name + XML_CHILDREN_VIEW;
                var data = loadtreexml(url);
                addNavigationTreeNodes(data, navTreeNode, 0);
                navTreeNode.isEmpty = 0;
                }
        if (navTreeNode.isCollapsed) {
	 	navTreeNode.expand();
                showChildren(elem);
   		}
        else {
                navTreeNode.collapse();
                hideChildren(elem);
   		}
        } 

function hideChildren(elem) {
        prettydump('hideChildren', LG_TRACE);
        var collections = elem.getElementsByTagName('collection');
        var num = collections.length;
	for (var i = num - 1; i >=0; i--) {
	        collections[i].style.display = 'none';
        	}
        }

function showChildren(elem) {
        prettydump('showChildren', LG_TRACE);
        var collections = elem.getElementsByTagName('collection');
        var num = collections.length;
        for (var i = num - 1; i >=0; i--) {
                var parentColl = getParentCollection(collections[i]);
                var parentNavTreeNode = navigationTree.getNodeByName(parentColl.getAttribute('name'));
                if (! (parentNavTreeNode.isCollapsed)) {
                        collections[i].style.display = 'block';
                        }
                }
        }

function getParentCollection(elem) {
        if (elem.getAttribute('isroot') != null) {
                throw "Root collection has no parent collection"; 
                }
        else {
                return elem.parentNode; 
                }
        }

function changeExpandIcon(elem, icon) {
        var expand = elem.getElementsByTagName('expand')[0];
        expand.style.backgroundImage = 'url("' + baseurl + '@@/' + icon + '")';
        }

//events
function mouseOverTree (e) {
        prettydump('mouseOverTree', LG_TRACE_EVENTS);
        var elem = getTreeEventTarget(e);
        if (elem.id == 'navtree') return;
        if (isTitle(elem)) {
	        elem.style.textDecoration = 'underline';
                var collectionElem = elem.parentNode.parentNode.parentNode;
                window.status = getTargetURL(collectionElem);
	        }
        }

function mouseOutTree (e) {
        prettydump('mouseOutTree', LG_TRACE_EVENTS);
        var elem = getTreeEventTarget(e);
        if (elem.id == 'navtree') return;
        if (isTitle(elem)) {
	        elem.style.textDecoration = 'none';
                window.status = '';
	        }
        }

function treeclicked (e) {
        prettydump('treeclicked', LG_TRACE_EVENTS);
        var elem = getTreeEventTarget(e);
        if (elem.id == 'navtree') return;
        // if node clicked is title elem, change page
        if (isTitle(elem)) {
	        location.href = getTargetURL(elem.parentNode.parentNode.parentNode);
	        }

        // if node clicked is expand elem, toggle expansion
        if (isExpand(elem)) {
                //get collection node
                elem = elem.parentNode;
                var navTreeNode = navigationTree.getNodeByName(elem.getAttribute('name'));
                toggleExpansion(navTreeNode);
                }
        }

// helpers

function getTargetURL(elem) {
        var location_href = baseurl;
	location_href = location_href + elem.getAttribute('name');
	location_href = location_href + CONTENT_VIEW;
        return location_href;
        }


function getControlPrefix() {
        if (getControlPrefix.prefix)
                return getControlPrefix.prefix;
   
        var prefixes = ["MSXML2", "Microsoft", "MSXML", "MSXML3"];
        var o, o2;
        for (var i = 0; i < prefixes.length; i++) {
                try {
                        // try to create the objects
                        o = new ActiveXObject(prefixes[i] + ".XmlHttp");
                        o2 = new ActiveXObject(prefixes[i] + ".XmlDom");
                        return getControlPrefix.prefix = prefixes[i];
                        }
                catch (ex) {};
                }
   
        throw new Error("Could not find an installed XML parser");
        }


// XmlHttp factory
function XmlHttp() {}


XmlHttp.create = function () {
if (window.XMLHttpRequest) {
        var req = new XMLHttpRequest();
         
        // some older versions of Moz did not support the readyState property
        // and the onreadystate event so we patch it!
        if (req.readyState == null) {
                req.readyState = 1;
                req.addEventListener("load", function () {
                                req.readyState = 4;
                                if (typeof req.onreadystatechange == "function")
                                req.onreadystatechange();}, false);
                }
 
                return req;
        }
if (window.ActiveXObject) {
        s = getControlPrefix() + '.XmlHttp';
        return new ActiveXObject(getControlPrefix() + ".XmlHttp");
        }
return;
};


function loadHandler () {
        // process document with dom methods
        alert(this.documentElement.nodeName);
        }

function loadtreexml (url) {
        var xmlHttp = XmlHttp.create(); 
        if (xmlHttp) {
                xmlHttp.open('GET', url, false); 
                xmlHttp.send(null);
                prettydump('Response XML ' + xmlHttp.responseText, LG_INFO);
                var data = xmlHttp.responseXML.documentElement;
                return data;
                }
        else {
                }
        }  

function loadtree (rooturl, thisbaseurl) {
        baseurl = rooturl;  // Global baseurl
  
	var url = thisbaseurl + SINGLE_BRANCH_TREE_VIEW;
        var data = loadtreexml(url);
        if (data) {
                var docNavTree = document.getElementById('navtreecontents');
                addNavigationTreeNodes(data, null, 1);
                docNavTree.appendChild(navigationTree.domNode);
                }
        }


function addNavigationTreeNodes(sourceNode, targetNavTreeNode, deep) {
        // create tree nodes from XML children nodes of sourceNode         
        // and add them to targetNode
        // if deep, create all descendants of sourceNode
        var basename = "";
        if (targetNavTreeNode) {
                basename = targetNavTreeNode.name;
                }
        var items = getCollectionChildNodes(sourceNode);
        var numitems = items.length;
        for (var i=0; i< numitems; i++) {
                var navTreeChild = createNavigationTreeNode(items[i], basename, deep);
                if (targetNavTreeNode) {
                        targetNavTreeNode.appendChild(navTreeChild);
                        }
                }
        }       

function getCollectionChildNodes(elem) {
        // get collection element nodes among childNodes of elem
        var items = elem.childNodes;
        var numitems = items.length;
        var currentItem;
        var result = new Array();
        for (var i = 0; i < numitems; i++) {
                currentItem = items[i];

                if (currentItem.nodeType != ELEMENT_NODE) {
                        continue;
                        }

                if (!isCollection(currentItem)) {
                        continue;
                        }
                result.push(currentItem);
                }
        return result;
        }


function createPresentationNodes(title, icon_url) {
        // create nodes hierarchy for one collection (without children)
        
        // create elem for plus/minus icon
        var expandElem = document.createElement('expand');
        // create elem for item icon
        var iconElem = document.createElement('icon');
        expandElem.appendChild(iconElem);
        iconElem.style.backgroundImage = 'url("' + icon_url + '")';
        // create title
        var titleElem = document.createElement('title');
        var newtextnode = document.createTextNode(title);
        
        titleElem.appendChild(newtextnode);
        
        iconElem.appendChild(titleElem);

        return expandElem;
        }

function createNavigationTreeNode(source, basename, deep) {
        var newelem = document.createElement(source.tagName);

        var navTreeNode = new navigationTreeNode(newelem);
        var elemName;
        var elemTitle;
        //XXX should not hardcode root folder name string
        if (source.getAttribute('isroot') != null) {
                elemTitle = '[top]';
                elemName = basename;
                newelem.style.marginLeft = '0px';
                navigationTree = navTreeNode;
                }
        else {
                elemTitle = source.getAttribute('name');
                elemName = basename + elemTitle + '/';
                }
        navTreeNode.setName(elemName);
        
        //could show number of child items
        //var length = source.getAttribute('length');
        //elemTitle = elemTitle + '(' + length + ')';
        
        var icon_url = source.getAttribute('icon_url');  

        
        var expandElem = createPresentationNodes(elemTitle, icon_url);
        newelem.appendChild(expandElem);


        if (deep) {
                var children = getCollectionChildNodes(source);
                var numchildren = children.length;
                for (var i=0; i< numchildren; i++) {
                        var navTreeNodeChild =  createNavigationTreeNode(children[i], navTreeNode.name, deep); 
                        var newchild = navTreeNodeChild.domNode;
                        newelem.appendChild(newchild);
                        navTreeNode.appendChild(navTreeNodeChild);
                        }
                if (numchildren) {
                        navTreeNode.isEmpty = 0;
                        navTreeNode.expand();
                        }
                else {
                        navTreeNode.isEmpty = 1;
                        navTreeNode.collapse();
                        }
                }
        else {
                navTreeNode.isEmpty = 1;
                navTreeNode.collapse();
                }
        return navTreeNode;
        }

