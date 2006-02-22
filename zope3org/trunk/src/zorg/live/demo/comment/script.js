
function makeParagraph(str) {
    str = str.replace(/\n/g, '<br/>');
    str = '<p>' + str + '</p>'
    return encodeURIComponent(str);
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
                                parameters:"comment=" + encodeURIComponent(value), 
                                asynchronous:true,
                                onComplete: function (request) {
                                    textUUID = $('update_feedback').innerHTML;
                                    }
                            }
                        )
                    }
                else {
                    sendEvent('update', {id: textUUID, html: makeParagraph(value)});
                    }
                }
            oldComment = value;
            }               
        );
}
