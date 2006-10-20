
var WikiMenu = {

    linkID : -1,
    extraInfo : "",
    caller : null,
    x : -1,
    
    dropDown : function(obj, e, dropmenuID, extra) {
    
        if (WikiMenu.linkID != -1) return
        
        WikiMenu.extraInfo = extra;
        if (WikiMenu.caller != obj) {
            WikiMenu.caller = obj
            WikiMenu.x = (document.all) ? window.event.x + document.body.scrollLeft  : e.pageX;
            }
      
        target = $(dropmenuID);
           
        if (window.event) 
            event.cancelBubble=true
        else if (e.stopPropagation) 
            e.stopPropagation()
        
        if (typeof dropmenuobj!="undefined") //hide previous menu
            dropmenuobj.style.visibility="hidden"
            clearhidemenu()
            if (ie5||ns6){
                obj.onmouseout=delayhidemenu
                dropmenuobj = target;
                if (hidemenu_onclick) 
                    dropmenuobj.onclick=function(){dropmenuobj.style.visibility='hidden'}
                dropmenuobj.onmouseover=clearhidemenu
                dropmenuobj.onmouseout=ie5? function(){ dynamichide(event)} : function(event){ dynamichide(event)}
                                
                showhide(dropmenuobj.style, e, "visible", "hidden")
              
                dropmenuobj.x= (WikiMenu.x != -1) ? WikiMenu.x : getposOffset(obj, "left")
                dropmenuobj.y= getposOffset(obj, "top")
                
                if ($("wiki_content")) {
                    var offsets = Position.positionedOffset($("wiki_content"))
                    dropmenuobj.x -= offsets[0];
                    dropmenuobj.y -= offsets[1];
                    }
             
                dropmenuobj.style.left=dropmenuobj.x-clearbrowseredge(obj, "rightedge")+"px"
                dropmenuobj.style.top=dropmenuobj.y-clearbrowseredge(obj, "bottomedge")+obj.offsetHeight+"px"
                }
        return clickreturnvalue()
        },
        
    close : function (event) {
        if ($('wiki_link_form').innerHTML) {
            $('wiki_link_form').innerHTML = "";
            }
        WikiMenu.linkID = -1;
        },
        
    alertReload : function () {
        alert("Reload");
        },
        
    editPlaceholderLabel : function (link_id, menu_id, label, extra) {
        WikiMenu.close();
        var newLabel = prompt('Enter a new label.',  label);
        if (newLabel) {
            var params = '&label=' + newLabel + extra;
            new Ajax.Updater('main', './@@modifyLink', 
                { parameters: 'cmd=rename&link_id='+ link_id + params,
                    asynchronous:true});
            }
        },

        
    submitForm : function (form) {
        
        new Ajax.Updater('main', './@@modifyLink', {
            parameters:Form.serialize(form),
            onError: function(request) { alert("Sorry, a server error occurred."); },
            onComplete: function(request) { WikiMenu.hideForm(); }
            });
            
        return false;  
        },
        
    showForm : function (cmd, id) {
       if (WikiMenu.linkID != id) {
            //WikiMenu.close();
           
            var timestamp =  $('modification_stamp').innerHTML;
            timestamp = timestamp.replace(/\+/g, '%2b');        // Obey + in datetime str format
            timestamp = "&modification_stamp=" + timestamp;
            
            new Ajax.Updater('wiki_link_form', './@@wikiCommandForm', 
                { parameters: 'cmd=' + cmd + '&menu_id='+ id + timestamp + WikiMenu.extraInfo});  

            WikiMenu.linkID = id;  
            WikiMenu.placeNextTo(WikiMenu.caller);
            }
        },
        
    hideForm : function () {
        WikiMenu.close();
        },
        
    placeNextTo : function(obj) {
        var offsets = Position.positionedOffset(obj)
        var x = offsets[0];
        var y = offsets[1];
        
        var form = $('wiki_link_form');
        form.style.left=x + "px";
        form.style.top=y + 15 + "px";
        }
    
}