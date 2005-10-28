//----------------------------------------------------------------------------
// DivMenu renders a nested list of <div> tags to a menu bar. See README.html 
// for a static sample.
// We move this javascript to zope.app.skintools.javascripts.divmenu later
//----------------------------------------------------------------------------

var menus = new Array(); // we put each menu in this Array

function DivMenu(id) {
    this.type = "horizontal";
    this.menuPosTop = 0;
    this.menuPosLeft = 0;
    this.subPosTop = 0;
    this.subPosLeft = 0;
    this.arrow = null;
    this.arrowOver = null;
    this.id = id;
    menus[self.id] = this;
    this.tree = new Array();
    this.visible = new Array();

    // Browser detection
    this.browser = {
        "ie": Boolean(document.body.currentStyle),
        "ie5": (navigator.appVersion.indexOf("MSIE 5.5") != -1 || navigator.appVersion.indexOf("MSIE 5.0") != -1)
    };
    if (!this.browser.ie) {
        this.browser.ie5 = false;
    }
}

/* Initialize the menu */
DivMenu.prototype.init = function() {
    document.onmousedown = this.click;
    if (this.browser.ie && this.browser.ie5) {
        this.fixWrap();
    }
    this.fixSections();
    this.parse(document.getElementById(this.id).childNodes, this.tree, this.id);
}

/* Search for menugroup elements and set width for them */
DivMenu.prototype.fixSections = function() {
    var arr = document.getElementById(this.id).getElementsByTagName("div");
    var menugroups = new Array();
    var widths = new Array();

    for (var i = 0; i < arr.length; i++) {
        if (arr[i].className == "menugroup") {
            menugroups.push(arr[i]);
        }
    }
    for (var i = 0; i < menugroups.length; i++) {
        widths.push(this.getMaxWidth(menugroups[i].childNodes));
    }
    for (var i = 0; i < menugroups.length; i++) {
        menugroups[i].style.width = (widths[i]) + "px";
    }
    if (menus[self.id].browser.ie) {
        for (var i = 0; i < menugroups.length; i++) {
            this.setMaxWidth(menugroups[i].childNodes, widths[i]);
        }
    }

}

DivMenu.prototype.fixWrap = function() {
    var elements = document.getElementById(this.id).getElementsByTagName("a");
    for (var i = 0; i < elements.length; i++) {
        if (/submenu/.test(elements[i].className)) {
            elements[i].innerHTML = '<div nowrap="nowrap">'+elements[i].innerHTML+'</div>';
        }
    }
}

/* Search for highest width */
DivMenu.prototype.getMaxWidth = function(nodes) {
    var maxWidth = 0;
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].nodeType != 1 || nodes[i].className == "menugroup") {
            continue;
        }
        if (nodes[i].offsetWidth > maxWidth) maxWidth = nodes[i].offsetWidth;
    }
    return maxWidth;
}

/* Set width for submenu elements */
DivMenu.prototype.setMaxWidth = function(nodes, maxWidth) {
    
    for (var i = 0; i < nodes.length; i++) {
        alert("nodes[i].tagName: " + nodes[i].outerHTML)
        if (nodes[i].nodeType == 1 && /submenu/.test(nodes[i].className) && nodes[i].currentStyle) {
            if (this.browser.ie5) {
                nodes[i].style.width = (maxWidth) + "px";
            } else {
                nodes[i].style.width = (maxWidth - parseInt(nodes[i].currentStyle.paddingLeft) - parseInt(nodes[i].currentStyle.paddingRight)) + "px"
            }
        }
    }
}

/* Parse menu structure, create events and position elements */
DivMenu.prototype.parse = function(nodes, tree, id) {
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].nodeType != 1) { continue };
        switch (nodes[i].className) {
            case "topmenu":
                nodes[i].id = id + "-" + tree.length;
                tree.push(new Array());
                nodes[i].onmouseover = this.topmenuOverShowsChilds;
                nodes[i].onclick = this.topmenuClick;
                break;
            case "submenu":
                nodes[i].id = id + "-" + tree.length;
                tree.push(new Array());
                nodes[i].onmouseover = this.submenuOver;
                nodes[i].onmouseout = this.submenuOut;
                nodes[i].onclick = this.submenuClick;
                break;
            case "menugroup":
                nodes[i].id = id + "-" + (tree.length - 1) + "-menugroup";
                var parentDiv = document.getElementById(id + "-" + (tree.length - 1));
                var childDiv = document.getElementById(nodes[i].id);
                var el = new DivMenuGroup(parentDiv.id);
                if (el.level == 1) {
                    if (this.type == "horizontal") {
                        childDiv.style.top = (parentDiv.offsetTop + parentDiv.offsetHeight + this.menuPosTop-3) + "px";
                        if (this.browser.ie5) {
                            childDiv.style.left = (2+this.menuPosLeft) + "px";
                        } else {
                            childDiv.style.left = (2+parentDiv.offsetLeft + this.menuPosLeft) + "px";
                        }
                    } else if (this.type == "vertical") {
                        childDiv.style.top = (parentDiv.offsetTop + this.menuPosTop) + "px";
                        if (this.browser.ie5) {
                            childDiv.style.left = (2+parentDiv.offsetWidth + this.menuPosLeft) + "px";
                        } else {
                            childDiv.style.left = (2+parentDiv.offsetLeft + parentDiv.offsetWidth + this.menuPosLeft) + "px";
                        }
                    }
                } else {
                    childDiv.style.top = (parentDiv.offsetTop + this.subPosTop-3) + "px";
                    childDiv.style.left = (2+parentDiv.offsetLeft + parentDiv.offsetWidth + this.subPosLeft) + "px";
                }
                break;
            case "menuarrow":
                nodes[i].id = id + "-" + (tree.length - 1) + "-menuarrow";
                break;
        }
        if (nodes[i].childNodes) {
            if (nodes[i].className == "menugroup") {
                this.parse(nodes[i].childNodes, tree[tree.length - 1], id + "-" + (tree.length - 1));
            } else {
                this.parse(nodes[i].childNodes, tree, id);
            }
        }
    }
}

/* Hide all menugroups */
DivMenu.prototype.hideAll = function() {
    for (var i = this.visible.length - 1; i >= 0; i--) {
        this.hide(this.visible[i]);
    }
}

/* Hide higher or equal levels */
DivMenu.prototype.hideHigherOrEqualLevels = function(n) {
    for (var i = this.visible.length - 1; i >= 0; i--) {
        var el = new DivMenuGroup(this.visible[i]);
        if (el.level >= n) {
            this.hide(el.id);
        } else {
            return;
        }
    }
}

/* Hide a menugroup */
DivMenu.prototype.hide = function(id) {
    var el = new DivMenuGroup(id);
    document.getElementById(id).className = (el.level == 1 ? "topmenu" : "submenu");
    if (el.level > 1 && this.arrowOver) {
        document.getElementById(id + "-menuarrow").src = this.arrow;
    }
    document.getElementById(id + "-menugroup").style.visibility = "hidden";
    document.getElementById(id + "-menugroup").style.zIndex = -1;
    if (this.visible.contains(id)) {
        if (this.visible[this.visible.length - 1] == id) {
            this.visible.pop();
        }
    }
}

/* Show a menugroup */
DivMenu.prototype.show = function(id) {
    var el = new DivMenuGroup(id);
    document.getElementById(id).className = (el.level == 1 ? "topmenu-active" : "submenu-active");
    if (el.level > 1 && this.arrowOver) {
        document.getElementById(id + "-menuarrow").src = this.arrowOver;
    }
    document.getElementById(id + "-menugroup").style.visibility = "visible";
    document.getElementById(id + "-menugroup").style.zIndex = 1;
    this.visible.push(id);
}

/* event, document.onmousedown */
DivMenu.prototype.click = function(e) {
    var el;
    if (e) {
        el = e.target.tagName ? e.target : e.target.parentNode;
    } else {
        el = window.event.srcElement;
        if (el.parentNode && /submenu/.test(el.parentNode.className)) {
            el = el.parentNode;
        }
    }
    if (!menus[self.id].visible.length) { return };
    if (!el.onclick) { menus[self.id].hideAll(); }
}

/* event, topmenu.onmouseover will show children*/
DivMenu.prototype.topmenuOverShowsChilds = function() {
    var el = new DivMenuGroup(this.id);
    menus[self.id].hideHigherOrEqualLevels(el.level);
    if (el.hasChilds()) {
        menus[self.id].show(this.id);
    }
}

/* event, topmenu.onmouseover */
DivMenu.prototype.topmenuOver = function() {
    if (!menus[self.id].visible.length) {
        return;
    }
    if (menus[self.id].visible.contains(this.id)) { return };
    menus[self.id].hideAll();
    var el = new DivMenuGroup(this.id);
    if (el.hasChilds()) {
        menus[self.id].show(this.id);
    }
}

/* event, topmenu.onclick */
DivMenu.prototype.topmenuClick = function() {
    this.blur();
    if (menus[self.id].visible.length) {
        menus[self.id].hideAll();
    } else {
        var el = new DivMenuGroup(this.id);
        if (el.hasChilds()) {
            menus[self.id].show(this.id);
        }
    }
}

/* event, submenu.onmouseover */
DivMenu.prototype.submenuOver = function() {
    var el = new DivMenuGroup(this.id);
    menus[self.id].hideHigherOrEqualLevels(el.level);
    if (el.hasChilds()) {
        menus[self.id].show(this.id);
    }
}

/* event, onmouseout hide all children */
DivMenu.prototype.mouseOutHideAll = function() {
    menus[self.id].hideAll();
}

/* event, submenu.onmouseout */
DivMenu.prototype.submenuOut = function() {
    var el = new DivMenuGroup(this.id);
    if (!el.hasChilds()) {
        document.getElementById(this.id).className = "submenu";
    }
}

/* event, submenu.onclick */
DivMenu.prototype.submenuClick = function() {
    this.blur();
    var el = new DivMenuGroup(this.id);
    menus[self.id].hideHigherOrEqualLevels(el.level);
    if (el.hasChilds()) {
        menus[self.id].show(this.id);
    }
}

/* DivMenuGroup */
function DivMenuGroup(id) {
    this.id = id;
    this.level = this.getLevel();
}

/* Get Level of given id */
DivMenuGroup.prototype.getLevel = function() {
    menu = menus[self.id]
    var s = this.id.substr(menu.id.length);
    return s.split("-").length - 1;
}


/* Check whether an element has a sub menugroup */
DivMenuGroup.prototype.hasChilds = function() {
    return Boolean(document.getElementById(this.id + "-menugroup"));
}

/* add missing Array function if needed (e.g. ie5) */
if (!Array.prototype.contains) {
    Array.prototype.contains = function(s) {
        for (var i = 0; i < this.length; i++) {
            if (this[i] == s) {
                return true;
            }
        }
        return false;
    }
}

if(!Array.prototype.copy) {
    Array.prototype.copy=function(a){
        var i = 0;
        var b = [];
        for(i;i<this.length;i++)
            b[i] = (typeof this[i].copy != 'undefined')?
                this[i].copy():
                this[i];
        return b
    };
}

if(!Array.prototype.concat) {
    Array.prototype.concat=function(a){
        var i = 0;
        var b = this.copy();
        for(i;i<a.length;i++) {
            b[b.length]=a[i];
        }
        return b
    };
}
    
if(!Array.prototype.pop) {
    Array.prototype.pop=function(){
      var response = this[this.length - 1]
      this.length--
      return response
    };
}

if(!Array.prototype.push) {
    Array.prototype.push=function(){
        var i = 0;
        var b = this.length;
        var a = arguments;
        for(i;i<a.length;i++) {
            this[b+i] = a[i];
        }
        return this.length
    };
}

if(!Array.prototype.shift) {
    Array.prototype.shift=function(){
        var i = 0;
        var b = this[0];
        for(i;i<this.length-1;i++) {
            this[i] = this[i+1];
        }
        this.length--;
        return b
    };
}

if(!Array.prototype.slice) {
    Array.prototype.slice=function(a,c){
        var i = 0;
        var b;
        var d = [];
        if(!c) {
            c=this.length;
        }
        if(c<0) {
            c=this.length+c;
        }
        if(a<0) {
            a=this.length-a;
        }
        if(c<a){
            b = a;
            a = c;
            c = b
        }
        for(i;i<c-a;i++)
            d[i] = this[a+i];
        return d
    };
}

if(!Array.prototype.splice) {
    Array.prototype.splice=function(a,c){
        var i = 0;
        var e = arguments;
        var d = this.copy();
        var f = a;
        if(!c) {
            c=this.length-a;
        }
        for(i;i<e.length-2;i++) {
            this[a+i]=e[i+2];
        }
        for(a;a<this.length-c;a++) {
            this[a+e.length-2]=d[a-c];
        }
        this.length-=c-e.length+2;
        return d.slice(f,f+c)
    };
}

if(!Array.prototype.unshift) {
    Array.prototype.unshift=function(a){
        var b;
        this.reverse();
        b = this.push(a);
        this.reverse();
        return b
    };
}
