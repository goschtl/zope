function dropdownlinkmenu(obj, e, dropmenuID)   {
    if (window.event) 
        event.cancelBubble=true
    else if (e.stopPropagation) 
        e.stopPropagation()
    hidelinkmenu(obj, e, dropmenuID)
    
    return clickreturnvalue()
}

function hidelinkmenu(obj, e, dropmenuID) {
    if (typeof dropmenuobj!="undefined") //hide previous menu
            
            dropmenuobj.style.visibility="hidden"
            clearhidemenu()
            if (ie5||ns6){
                obj.onmouseout=delayhidemenu
                dropmenuobj=document.getElementById(dropmenuID)
                if (hidemenu_onclick) dropmenuobj.onclick=function(){dropmenuobj.style.visibility='hidden'}
                dropmenuobj.onmouseover=clearhidemenu
                dropmenuobj.onmouseout=ie5? function(){ dynamichide(event)} : function(event){ dynamichide(event)}
                
                
                showhide(dropmenuobj.style, e, "visible", "hidden")

                var offsets = Position.cumulativeOffset(obj)
                
                var x = offsets[0]  // offsets[0]-clearbrowseredge(obj, "leftedge")+"px"
                var y = offsets[1]
                
                if (dropmenuobj.y) {
                    y = Math.max(Event.pointerY(e), dropmenuobj.y, y)  // -clearbrowseredge(obj, "bottomedge")+obj.offsetHeight+"px"
                    }
                
                dropmenuobj.x=x
                dropmenuobj.y=y

                dropmenuobj.style.left=x + "px"
                dropmenuobj.style.top=y + "px"
            }
}            


function editPlaceholderLabel(link_id, menu_id, label, extra) {
    
     var newLabel = prompt('Enter a new label.',  label);
   
     if (newLabel) 
        {
        new Ajax.Updater('main', './@@modifyLink', { parameters: 'cmd=rename&link_id='+ link_id + '&label=' + newLabel + extra, asynchronous:true});
        }

}



