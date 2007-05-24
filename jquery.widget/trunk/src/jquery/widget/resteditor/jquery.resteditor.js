//----------------------------------------------------------------------------
/** 
 * @fileoverview RESTEditor implementation 
 * @author Roger Ineichen roger@projekt01.ch
 * @version Initial, not documented 
 */
//----------------------------------------------------------------------------
/* zrt-replace: "./img" tal"string:${context/++resource++jqueryRestEditorIMG}" */

var RESTEditorToolBarButtons = new Array(); // array of buttons

//---[ image resources ]-------------------------------------------------------
var restEditorBold = './img/restEditorBold.gif';
var restEditorItalic = './img/restEditorItalic.gif';
var restEditorLink = './img/restEditorLink.gif';
var restEditorCode = './img/restEditorCode.gif';
var restEditorRule = './img/restEditorRule.gif';
var restEditorBoldActive = './img/restEditorBoldActive.gif';
var restEditorItalicActive = './img/restEditorItalicActive.gif';
var restEditorLinkActive = './img/restEditorLinkActive.gif';
var restEditorCodeActive = './img/restEditorCodeActive.gif';
var restEditorRuleActive = './img/restEditorRuleActive.gif';


function RESTEditorToolBarButton(id, imgSrc, activeImgSrc) {
    this.id = id;
    this.imgSrc = imgSrc;
    this.activeImgSrc = activeImgSrc;
}


function RESTEditorToolBar(id) {
    this.id = id;
}

RESTEditorToolBar.prototype.init = function() {
    var self = this;
    this.textarea = document.getElementById(this.id);
    if ((typeof(document["selection"]) == "undefined")
        && (typeof(this.textarea["setSelectionRange"]) == "undefined")) {
        return;
    }
    this.resteditor = document.createElement("div");
    this.resteditor.className = 'RESTEditorToolBar';
    
    id = 'bold'
    title = "Bold text: **Example**"
    this.addButton(id, title, restEditorBold, restEditorBoldActive, function() {
        self.encloseSelection("**", "**");
    });

    id = 'italic'
    title = "Italic text: *Example*"
    this.addButton(id, title, restEditorItalic, restEditorItalicActive, function() {
        self.encloseSelection("*", "*");
    });

    id = 'link'
    title = "Link: [http://www.example.com/ Example]"
    this.addButton(id, title, restEditorLink, restEditorLinkActive, function() {
        self.encloseSelection("[", "]");
    });

    id = 'code'
    title = "Code block: {{{ example }}}"
    this.addButton(id, title, restEditorCode, restEditorCodeActive, function() {
        self.encloseSelection("\n::\n\n  ", "\n");
    });

    id = 'rule'
    title = "Horizontal rule: ----"
    this.addButton(id, title, restEditorRule, restEditorRuleActive, function() {
        self.encloseSelection("\n----\n", "");
    });
    this.textarea.parentNode.insertBefore(this.resteditor, this.textarea);
}

RESTEditorToolBar.prototype.encloseSelection = function(prefix, suffix) {
    textarea = this.textarea;
    this.textarea.focus();
    var start, end, sel, scrollPos, subst;
    if (typeof(document["selection"]) != "undefined") {
        sel = document.selection.createRange().text;
    } else if (typeof(textarea["setSelectionRange"]) != "undefined") {
        start = textarea.selectionStart;
        end = textarea.selectionEnd;
        scrollPos = textarea.scrollTop;
        sel = textarea.value.substring(start, end);
    }
    if (sel.match(/ $/)) { // exclude ending space char
        sel = sel.substring(0, sel.length - 1);
        suffix = suffix + " ";
    }
    subst = prefix + sel + suffix;
    if (typeof(document["selection"]) != "undefined") {
        var range = document.selection.createRange().text = subst;
        textarea.caretPos -= suffix.length;
    } else if (typeof(textarea["setSelectionRange"]) != "undefined") {
        textarea.value = textarea.value.substring(0, start) + subst +  
            textarea.value.substring(end);
      if (sel) {
            textarea.setSelectionRange(start + subst.length, start + subst.length);
      } else {
            textarea.setSelectionRange(start + prefix.length, start + prefix.length);
      }
      textarea.scrollTop = scrollPos;
    }
}


RESTEditorToolBar.prototype.addButton = function(id, title, imgSrc, activeImgSrc, fn) {
    var btn = new RESTEditorToolBarButton(id, imgSrc, activeImgSrc)
    var a = document.createElement("A");
    var img = document.createElement("IMG");
    RESTEditorToolBarButtons[id] = btn;
    img.id = id;
    a.href = "#";
    a.title = title;
    $(a).click(fn);
    $(a).mouseover(function(e) {
        if (e) {
            ele = e.target.tagName ? e.target : e.target.parentNode;
        } else {
            ele = window.event.srcElement;
        }
        btn = RESTEditorToolBarButtons[ele.id];
        activeImgSrc = btn.activeImgSrc;
        ele.src = activeImgSrc;
        return false;
    });
    $(a).mouseout(function(e) {
        if (e) {
            ele = e.target.tagName ? e.target : e.target.parentNode;
        } else {
            ele = window.event.srcElement;
        }
        btn = RESTEditorToolBarButtons[ele.id];
        imgSrc = btn.imgSrc;
        ele.src = imgSrc;
        return false;
    });
    a.tabIndex = 9999;
    img.src = imgSrc;
    img.alt = title;
    a.appendChild(img);
    this.resteditor.appendChild(a);
}

jQuery.fn.restEditor = function() {
  return this.each(function(){
    var editor = new RESTEditorToolBar(this.id);
    editor.init();
  });
};

