
var PopupMenu = {

    dropmenuID : "",

    initialize : function() {
        document.onmousedown = PopupMenu.onMouseDown;
        },
            
    update : function (caller, dropmenuID)  {
        document.onmousedown = PopupMenu.onMouseDown;
        if (PopupMenu.dropmenuID != dropmenuID) {
            PopupMenu.close();
            var timestamp =  $('modification_stamp').innerHTML;
            timestamp = timestamp.replace(/\+/g, '%2b');        // Obey + in datetime str format
            timestamp = "&modification_stamp=" + timestamp;
            
            new Ajax.Updater('wiki_popup_menu', './@@popupLinkMenu', 
                { parameters: 'menu_id='+ dropmenuID + timestamp});
            PopupMenu.dropmenuID = dropmenuID  
            PopupMenu.placeNextTo(caller);
            }
        },

    close : function (event) {
        if ($('wiki_popup_menu').innerHTML) {
            $('wiki_popup_menu').innerHTML = "";
            }
        PopupMenu.dropmenuID = "";
        },
        
    alertReload : function () {
        alert("Reload");
        },
        
    editPlaceholderLabel : function (link_id, menu_id, label, extra) {
        PopupMenu.close();
        var newLabel = prompt('Enter a new label.',  label);
        if (newLabel) {
            var params = '&label=' + newLabel + extra;
            new Ajax.Updater('main', './@@modifyLink', 
                { parameters: 'cmd=rename&link_id='+ link_id + params,
                    asynchronous:true});
            }
        },

        
    submitForm : function (id, form) {
        new Ajax.Updater('main', './@@modifyLink', {
            parameters:Form.serialize(form),
            onError: function(request) { alert("Sorry, a server error occurred."); },
            onComplete: function(request) { PopupMenu.hideForm(id); }
            });
        return false;  
        },
        
    showForm : function (id) {
        Element.hide('popup_items');
        Element.show(id);
        },
        
    hideForm : function (id) {
        Element.hide(id);
        PopupMenu.close();
        },
        
    placeNextTo : function(obj) {
        var offsets = Position.positionedOffset(obj)
                
        var x = offsets[0];
        var y = offsets[1];
        var menu = $('wiki_popup_menu');
        menu.style.left=x + "px";
        menu.style.top=y + 15 + "px";
        },
    
    
    onMouseDown : function (event) {
        if (!event) var event = window.event; // IE compatibility
        
        if (event.target) {
            targ = event.target;
            }
        else if (event.srcElement) {
            targ = event.srcElement;
            }
        
        var node = targ;
        while (node) {
            if (node == $('wiki_popup_menu')) {
                return;
                }
            node = node.parentNode;
            }
            
        PopupMenu.close();
        }
}


window.onload = PopupMenu.initialize;

