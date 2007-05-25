//----------------------------------------------------------------------------
/** 
 * @fileoverview JSON-RPC based live search implementation
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version Initial, not documented 
 */
//----------------------------------------------------------------------------

function setLiveSearchResult(response) {
    // we use a default element id, use a custom callback if this doesn't fit
    ele = $('#liveSearchResultContainer');
    if (response.content != null) {
        $(ele).html(response.content)
        $(ele).show('fast')
    } else {
        $(ele).hide('fast')
    }
}

function closeLiveSearchResult(id) {
    $('#'+id).hide();
}

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------
/**
 * apply live search functionality. *
 * @name     jsonLiveSearch
 * @name     json live search with callback
 * @param    settings Hash with the following options:
 *               jsonURL   The url where the json view getLiveSearchResult is available
 *               minQueryLenght The min length of the query string before we call json search
 *               resultElementExpression The xpath expresseion for get the result element
 *               requestId The is passed to the server via json, can be used for identify a search wquery
 *               searchMethodName The json search method name, can be used if you need to call different json views
 *               callback  The callback function which get called within the response as argument
 * @author   Roger Ineichen dev - projekt01 - ch
 * @example  $("#myInputField").jsonLiveSearch();
 * @example  $("#myInputField").jsonLiveSearch({url:'http://localhost/page'});
 * @example  $("#myInputField").jsonLiveSearch({url:'http://localhost/page', callback:setLiveSearchResult});
 */
jQuery.fn.jsonLiveSearch = function(settings) {
    settings = jQuery.extend({
        jsonURL: contextURL,
        minQueryLenght: 2,
        resultElementExpression: '#liveSearchResultContainer',
        requestId: 'jsonLiveSearch',
        searchMethodName: 'getLiveSearchResult',
        callback: setLiveSearchResult
    }, settings);
    return this.each(function(){
        $(this).keyup(function(){
        	value = $(this).val();
        	if (value != '' && value.length >= settings.minQueryLenght) {
            	var proxy = getJSONRPCProxy(settings.jsonURL);
            	proxy.addMethod(settings.searchMethodName, settings.callback, settings.requestId);
            	proxy[settings.searchMethodName](value);
            }else {
                $(settings.resultElementExpression).hide();
            }
        });

    });
};

