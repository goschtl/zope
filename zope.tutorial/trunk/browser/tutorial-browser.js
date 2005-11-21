var commands = {};

function getContentDocument() {
    return frames['tutorial-content'].document;
}

function setHighlighted(element) {
    element.style.border = "1px red solid";
}

function setOriginal(element, original) {
    element.style.border = original;
}

function blinkElement(element) {
    var original = element.style.border;

    frames['tutorial-content'].setTimeout("setHighlighted(element)", 1000);
    frames['tutorial-content'].setTimeout("setOriginal(element, original)", 1000);
}

function nullAction() {
}
commands['nullAction'] = nullAction;

function displayText(text) {
    div = bot.locateElementByIdentifier('tutorial-text', document);
    div.innerHTML = text;
}
commands['displayText'] = displayText;


function finishTutorial() {
    displayText(Array(''));
    stopTutorial();
}
commands['finishTutorial'] = finishTutorial

/* ------------------------------------------------------------------------ */

function openUrl(url) {
    iframe = bot.locateElementByIdentifier('tutorial-content', document);
    iframe.contentDocument.location.href = url;
    return url
}
commands['openUrl'] = openUrl;

function getUrl() {
    iframe = bot.locateElementByIdentifier('tutorial-content', document);
    return iframe.contentDocument.location.href;
}
commands['getUrl'] = getUrl;

function getTitle() {
    iframe = bot.locateElementByIdentifier('tutorial-content', document);
    return iframe.contentDocument.title;
}
commands['getTitle'] = getTitle;

function getContent() {
    // TODO: There seems to be no way of getting the entire source. Sigh. :-(
    iframe = bot.locateElementByIdentifier('tutorial-content', document);
    return iframe.contentDocument.body.innerHTML;
}
commands['getContent'] = getContent;

function reload() {
    iframe = bot.locateElementByIdentifier('tutorial-content', document);
    return iframe.contentDocument.location.reload()
}
commands['reload'] = reload;

function goBack(steps) {
    for (x=0; x<steps; x++) {
        frames['tutorial-content'].history.back()
    }
}
commands['goBack'] = goBack;



function clickLink(text, url, id) {
    if (text) {
        link = contentBot.findElementByTagNameAndText(
            getContentDocument(), 'a', text);
    }

      if (url) {
        link = contentBott.findElementByTagNameAndAttributeValue(
            getContentDocument(), 'a', 'href', url);
    }

    if (id) {
        link = contentBot.locateElementByIdentifier(
            'tutorial-content', getContentDocument());
    }
    blinkElement(link);
    contentBot.clickElement(link);
}
commands['clickLink'] = clickLink;
