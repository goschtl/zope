//----------------------------------------------------------------------------
// DivMenu renders a nested list of <div> tags to a menu bar. See index.html 
// for a static sample.
//----------------------------------------------------------------------------

(function($) {
$.fn.z3cDivMenu = function (settings) {
    settings = $.extend({
        contentURL: false
    }, settings);

    var menuType = "horizontal";
    var menuPosTop = 0;
    var menuPosLeft = 0;
    var subPosTop = 0;
    var subPosLeft = 0;
    var divMenuArrow = null;
    var divMenuArrowOver = null;
    var stackTopMenu = null;
    var tree = new Array();
    var visible = new Array();

    // Browser detection
    var browser = {
        "ie": Boolean(document.body.currentStyle)
    };
    /* Search for menuGroup elements and set width for them */
    function fixSections(ele) {
        var arr = $(ele).find('div');
        var menuGroups = new Array();
        var widths = new Array();
    
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].className == "menuGroup") {
                menuGroups.push(arr[i]);
            }
        }
        for (var i = 0; i < menuGroups.length; i++) {
            widths.push(getMaxWidth(menuGroups[i].childNodes));
        }
        for (var i = 0; i < menuGroups.length; i++) {
            menuGroups[i].style.width = (widths[i]) + "px";
        }
        if (browser.ie) {
            for (var i = 0; i < menuGroups.length; i++) {
                setMaxWidth(menuGroups[i].childNodes, widths[i]);
            }
        }
    
    }

    /* Search for highest width */
    function getMaxWidth(nodes) {
        var maxWidth = 0;
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].nodeType != 1 || nodes[i].className == "menuGroup") {
                continue;
            }
            if (nodes[i].offsetWidth > maxWidth) {
                maxWidth = nodes[i].offsetWidth;
            }
        }
        return maxWidth;
    }

    /* Set width for subMenu elements */
    function setMaxWidth(nodes, maxWidth) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].nodeType == 1 && /subMenu/.test(nodes[i].className) && nodes[i].currentStyle) {
                widthCSS = (maxWidth - parseInt(nodes[i].currentStyle.paddingLeft) - parseInt(nodes[i].currentStyle.paddingRight)) + "px";
                $(nodes[i]).css('width', widthCSS);
            }
        }
    }

    function hasChilds(ele) {
        return $('#' +ele.id + "-menuGroup").is("div");
    }

    /* Hide all visible elements */
    function hideAll() {
        for (var i = visible.length - 1; i >= 0; i--) {
            hideElement($('#'+visible[i]).get(0));
        }
    }

    /* get level */
    function getLevel(id) {
        if (!id) {return false};
        var menuId = 'z3cDivMenu'
        var s = id.substr(menuId.length);
        return s.split("-").length - 1;
    }


    /* Hide higher or equal levels */
    function hideHigherOrEqualLevels(ele) {
        var level = getLevel(ele.id);
        for (var i = visible.length - 1; i >= 0; i--) {
            visibleLevel = getLevel($('#'+visible[i]).get(0).id);
            if (visibleLevel && visibleLevel >= level) {
                hideElement($('#'+visible[i]).get(0));
            }
        }
    }

    /* Hide a menu element */
    function hideElement(ele) {
        if (ele.className == 'topMenuActive') {
            $(ele).removeClass('topMenuActive');
            $(ele).addClass('topMenu');
            if (divMenuArrowOver) {
                $('menuArrow').src = divMenuArrow;
            }
        } else if (ele.className == 'subMenuActive') {
            $(ele).removeClass('subMenuActive');
            $(ele).addClass('subMenu');
        }
        menuGroup = $('#' +ele.id + "-menuGroup");
        $(menuGroup).css('visibility', 'hidden');
        $(menuGroup).css('z-index', -1);
        for (var i = visible.length - 1; i >= 0; i--) {
            if (visible[visible.length - 1] == ele.id) {
                visible.pop();
            }
        }
    }

    function topMenuOver(ele) {
        hideHigherOrEqualLevels(ele);
        if (hasChilds(ele)) {
            $(ele).removeClass('topMenu');
            $(ele).addClass('topMenuActive');
            if (divMenuArrowOver) {
                $('#'+ele.id+'-menuArrow').attr('src', divMenuArrowOver);
            }
            menuGroup = $('#' +ele.id + "-menuGroup");
            $(menuGroup).css('visibility', 'visible');
            $(menuGroup).css('z-index', 1);
            visible.push(ele.id);
        }
    }

    function subMenuOver(ele) {
        hideHigherOrEqualLevels(ele);
        $(ele).removeClass('subMenu');
        $(ele).addClass('subMenuActive');
        if (divMenuArrowOver) {
            $('#'+ele.id+'-menuArrow').attr('src', divMenuArrowOver);
        }
        menuGroup = $('#' +ele.id + "-menuGroup");
        $(menuGroup).css('visibility', 'visible');
        $(menuGroup).css('z-index', 1);
        visible.push(ele.id);
    }
    
    function subMenuOut(ele) {
        if (!hasChilds(ele)) {
            $(ele).removeClass('subMenuActive');
            $(ele).addClass('subMenu');
        }
    }

    function subMenuClick(ele) {
        hideHigherOrEqualLevels(ele);
        if (!hasChilds(ele)) {
            hideHigherOrEqualLevels(ele);
            showElement(ele);
        }
        return false;
    }

    function renderElement(self, tree, id) {
        for (var i = 0; i < self.childNodes.length; i++) {
            var ele = self.childNodes[i];
            if (ele.nodeType != 1) {
                continue
            };
            switch (ele.className) {
                case "topMenu":
                    stackTopMenu = ele;
                    $(ele).attr('id', id + "-" + tree.length);
                    tree.push(new Array());
                    $(ele).bind('mouseover', function() {
                        topMenuOver(this);
                    });
                    break;
                case "subMenu":
                    $(ele).attr('id', id + "-" + tree.length);
                    tree.push(new Array());
                    $(ele).bind('click', function(e) {
                        e.stopPropagation();
                        subMenuClick(this);
                    });
                    $(ele).bind('mouseout', function() {
                        subMenuOut(this);
                    });
                    $(ele).bind('mouseover', function() {
                        subMenuOver(this);
                    });
                    break;
                case "menuGroup":
                    level = getLevel(id);
                    parentBox = $('#'+ id + "-" + (tree.length - 1)).get(0);
                    $(ele).attr('id', id + "-" + (tree.length - 1) + "-menuGroup");
                    var parentDiv = stackTopMenu;
                    if (level == 0) {
                        if (menuType == "horizontal") {
                            topCSS = menuPosTop + parentDiv.offsetTop + parentDiv.offsetHeight -3;
                            leftCSS = 2 + menuPosLeft + parentDiv.offsetLeft;
                        } else if (menuType == "vertical") {
                            topCSS = menuPosTop + parentDiv.offsetTop;
                            leftCSS = 2 + menuPosLeft + parentDiv.offsetLeft + parentDiv.offsetWidth;
                        }
                    } else {
                        topCSS = parentBox.offsetTop + subPosTop;
                        leftCSS = 2 + parentBox.offsetLeft + parentBox.offsetWidth + subPosLeft;
                    }
                    $(ele).css('top', topCSS);
                    $(ele).css('left', leftCSS);
                    break;
                case "menuArrow":
                    $(ele).attr('id', id + "-" + (tree.length - 1) + "-menuArrow");
                    break;
            }
            if (ele.childNodes) {
                if (ele.className == "menuGroup") {
                    renderElement(ele, [tree.length - 1], id + "-" + (tree.length - 1));
                } else {
                    renderElement(ele, tree, id);
                }
            }
        }
    }

    function renderMenu(ele) {
        fixSections(ele);
        renderElement(ele, tree, ele.id);
       $(document).bind('click', function(){
            hideAll();
        })
    }

    // render menu
    return $(this).each(function(){
        renderMenu(this);
    });
};
})(jQuery);
