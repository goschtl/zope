var dtwLanguageLoaded = false;

function dateTimeWidgetLoadLanguageFile(url){

    // this method loads a languagefile for the datetimewidget
    // TODO: move this functinality into zc.resourcelibrary
    
    if (dtwLanguageLoaded==true){
        return;
    }
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    document.getElementsByTagName('head')[0].appendChild(script);
    dtwLanguageLoaded = true;
}


