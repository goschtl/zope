var CurrentTutorial = '';
var SessionId = '';
var ServerConnection = null;

var bot = null;
var contentBot = null;

function toggleDisplayElement(id) {

    element = bot.locateElementByIdentifier(id, document)

    // Reference the style ...
    if (element.style) {
        style = element.style;
    }

    if (typeof(style.display) == 'undefined' &&
        !( window.ScriptEngine && ScriptEngine().indexOf('InScript') + 1 ) ) {
        //The browser does not allow us to change the display style
        //Alert something sensible (not what I have here ...)
        window.alert( 'Your browser does not support this' );
        return;
    }

   // Change the display style
    if (style.display != '') {
        style.display = '';
   }
    else {
        style.display = 'none'
    }
}

function initializeTutorialRunner() {
    /* Create bots */
    bot = PageBot.createForWindow(window);
    contentBot = PageBot.createForWindow(frames['tutorial-content']);
}

function startTutorial() {
    CurrentTutorial = bot.locateElementByIdentifier(
        'tutorial-selector', document).value;
    toggleDisplayElement('start-button');
    toggleDisplayElement('stop-button');
    toggleDisplayElement('next-button');

    /* Create a session */
    var addr = document.URL + CurrentTutorial + '/++sessions++/'
    var jsonrpc = importModule("jsonrpc");
    var server = new jsonrpc.ServiceProxy(addr, ['createSession']);
    SessionId = server.createSession()

    /* Create a new server connection to the session */
    var addr = document.URL + CurrentTutorial + '/++sessions++' + SessionId
        ServerConnection = new jsonrpc.ServiceProxy(
        addr, ['getNextStep', 'setCommandResult', 'keepGoing']);
}

function stopTutorial() {
    /* Delete the session */
    addr = document.URL + CurrentTutorial + '/++sessions++/'
    var jsonrpc = importModule("jsonrpc");
    var server = new jsonrpc.ServiceProxy(addr, ['deleteSession']);
    server.deleteSession(SessionId);

    CurrentTutorial = '';
    SessionId = '';
    ServerConnection = null;
    toggleDisplayElement('start-button');
    toggleDisplayElement('stop-button');
    toggleDisplayElement('next-button');
}

function runNextStep() {
    var keepGoing = true;
    while (keepGoing) {
        command = ServerConnection.getNextStep();
        result = commands[command.action].apply(null, command.params);
        answer = ServerConnection.setCommandResult(result);
        keepGoing = ServerConnection.keepGoing();
    }
}
