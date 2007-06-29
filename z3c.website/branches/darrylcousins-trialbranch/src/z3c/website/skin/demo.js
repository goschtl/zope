function setWebSiteLiveSearchResult(response) {
    // we use a default element id, use a custom callback if this doesn't fit
    ele = $('#webSiteLiveSearchResultContainer');
    if (response.content != null) {
        $(ele).html(response.content)
        $(ele).show('fast')
    } else {
        $(ele).hide('fast')
    }
}

$(document).ready(function() {
    // note: we use a none leaking fixed version of the fisheye menu, ri
    $('#dock').Fisheye(
        {maxWidth: 60,
         itemWidth: 53,
         proximity: 90,
         halign : 'center'}
    );
    $('form#JSONValidateSample input').jsonValidate();
    $('form#JSONValidateSample textarea').jsonValidate();
    $('textarea.restEditorWidget').restEditor();
    $('#liveSearchInput').jsonLiveSearch();
    settings = {searchMethodName:'getWebSiteLiveSearchResult',
                callback: setWebSiteLiveSearchResult,
                resultElementExpression: '#webSiteLiveSearchResultContainer'}
    $('#webSiteLiveSearchInput').jsonLiveSearch(settings);
    $('.naviBox').corner();
});
