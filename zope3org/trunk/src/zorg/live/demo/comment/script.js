
function escapeValue(str) {
    str = str.replace(/\&/g, '%26');
    return str.replace(/\+/g, '%2b')
}

function makeParagraph(str) {
    str = escapeValue(str);
    str = str.replace(/\n/g, '<br/>');
    return '<p>' + str + '</p>'
}


var textUUID = "";

function installTextObserver()
{
    new Form.Element.Observer('commentbox', 1, 
        function(element, value) {
            if (value) {
                if (textUUID == "") {
                    new Ajax.Updater('update_feedback', './@@startComment', 
                            { 
                                parameters:"comment=" + escapeValue(value), 
                                asynchronous:true,
                                onComplete: function (request) {
                                    textUUID = $('update_feedback').innerHTML;
                                    }
                            }
                        )
                    }
                else {
                    sendLivePage('update', textUUID, makeParagraph(value));
                    }
                }
            oldComment = value;
            }               
        );
}
