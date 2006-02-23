
function makeParagraph(str) {
    str = str.replace(/\n/g, '<br/>');
    str = '<p>' + str + '</p>'
    return encodeURIComponent(str);
}

var currentCommentKey = "";

function installTextObserver() {
    new Form.Element.Observer('commentbox', 1, 
        function(element, value) {
            if (value) {
                if (currentCommentKey == "") {
                    new Ajax.Updater('update_feedback', './@@addComment', { 
                            parameters:"text=" + encodeURIComponent(value), 
                            asynchronous:true,
                            onComplete: function (request) {
                                currentCommentKey = $('update_feedback').innerHTML;
                                }
                        })
                    }
                else {
                    sendEvent('update', {
                            id: "text"+currentCommentKey, 
                            html: makeParagraph(value),
                            extra: "scroll"
                        });
                    }
                }
            }               
        );
    }
    


function saveComment(textarea) {
    var text = textarea.value;
    
    new Ajax.Updater('update_feedback', './@@saveComment', {
                parameters: "key:int=" + currentCommentKey + "&text=" + encodeURIComponent(text), 
                onComplete: function (request) {
                                currentCommentKey = "";
                                textarea.value = "";
                                }
                } );
    return false;
    }

function cancelComment() {
   
    new Ajax.Updater('update_feedback', './@@cancelComment', {
                parameters: "key:int=" + currentCommentKey, 
                onComplete: function (request) {
                                currentCommentKey = "";
                                }
                
                });
    return false;
    }