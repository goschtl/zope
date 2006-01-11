// ===========================================================================
// COMMENT FUNCTIONS
// ===========================================================================


function showAddCommentWindow() {
    var features='screenX=445,screenY=220,height=400,width=700,scrollbars=1,' +
                'dependent=0,directories=0,fullscreen=0,location=0,menubar=0,' +
                'resizeable=0,status=0,toolbar=0';
    
    var win = window.open("wikiaddcomment.html", "Add Comment", features);
    win.focus();
    return true;
}

