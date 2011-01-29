dojo.require('dijit.form.Button');
dojo.require('dijit.form.ValidationTextBox');
dojo.require('dijit.form.ComboButton');
dojo.require('dijit.Menu');
dojo.require('dijit.MenuItem');

var web_frame_application = {
    playing: true,
    urls: [],
    menu_items: {},
    index: 0,
    key: 'web_frame_application' +
        window.location.pathname + window.location.search,
    play1: function (noinc) {
        if (! noinc) {
            web_frame_application.index += 1;
        }
        if ((noinc || web_frame_application.playing) &&
            web_frame_application.urls.length
           ) {
            while (web_frame_application.index < 0) {
                web_frame_application.index += (
                    web_frame_application.urls.length);
            }
            dojo.byId('frame').src = web_frame_application.urls[
                web_frame_application.index %
                    web_frame_application.urls.length];
        }
    },
    back: function () {
        if (web_frame_application.playing) {
            web_frame_application.toggle();
        }
        web_frame_application.index -= 1;
        web_frame_application.play1(true);
    },
    forward: function () {
        web_frame_application.index += 1;
        web_frame_application.play1(true);
    },
    toggle: function () {
        var toggle_button = dojo.byId('playtoggle');
        if (web_frame_application.playing) {
            web_frame_application.playing = false;
            toggle_button.innerHTML = "\u25b6";
            toggle_button.title = "Play";
        }
        else {
            web_frame_application.playing = true;
            toggle_button.innerHTML = "&nbsp;&#x2016;&nbsp;";
            toggle_button.
            toggle_button.title = "Stop";
            web_frame_application.play1();
        }
    },
    play_url: function (src) {
        dojo.byId('frame').src = src;
        web_frame_application.index = dojo.indexOf(
            web_frame_application.urls, src);
    },
    enter: function (value) {
        if (! (/^\w+:/.exec(value))) {
            value = 'http://' + value;
        }
        dojo.byId('frame').src = value;
        web_frame_application.update_controls();
    },
    add: function () {
        dijit.byId('url').set('value', '');
        var src = dojo.byId('frame').src, item;
        if (src)
        {
            if (dojo.indexOf(web_frame_application.urls, src) >= 0) {
                alert("Already in urls: "+src);
            }
            else {
                web_frame_application.urls.push(src);
                item = new dijit.MenuItem(
                    {
                        label: src,
                        onClick: function () {
                            web_frame_application.play_url(src);
                        }
                    }
                );
                dijit.byId("url_menu").addChild(item);
                web_frame_application.menu_items[src] = item;
                localStorage.setItem(
                    web_frame_application.key,
                    JSON.stringify(web_frame_application.urls));
            }
        }
        else {
            alert("You must be viewing a url.");
        }
        web_frame_application.update_controls();
    },
    remove: function () {
        var index, src = dojo.byId('frame').src;
        if (src)
        {
            index = dojo.indexOf(web_frame_application.urls, src);
            if (index >= 0) {
                web_frame_application.urls.splice(index, 1);
                web_frame_application.menu_items[src].destroy();
                delete web_frame_application.menu_items[src];
                web_frame_application.play1(false);
                localStorage.setItem(
                    web_frame_application.key,
                    JSON.stringify(web_frame_application.urls));
            }
            else {
                alert("This isn't a saved url in the first place.");
            }
        }
        else {
            alert("You must be viewing a url.");
        }
        web_frame_application.update_controls();
        dojo.byId('frame').src = '';
    },
    update_controls: function () {
        var index, src = dojo.byId('frame').src;
        if (src) {
            index = dojo.indexOf(web_frame_application.urls, src);
        }
        dijit.byId('add').set('disabled', ! (src && index < 0));
        dijit.byId('remove').set('disabled', ! (src && index >= 0));
        dijit.byId('back').set('disabled',
                              ! (web_frame_application.urls.length));
        dijit.byId('forward').set('disabled',
                                 ! (web_frame_application.urls.length));
        dijit.byId('playtoggle').set('disabled',
                                    ! (web_frame_application.urls.length));

    }
}

dojo.addOnLoad(
    function () {
        var urls;
        urls = localStorage.getItem(web_frame_application.key);
        if (urls) {
            urls = JSON.parse(urls);
        }
        else {
            urls = [];
        }
        web_frame_application.urls = urls;
        function player () {
            web_frame_application.play1();
            setTimeout(player, 60000);
        }
        player();
        web_frame_application.update_controls();

        dojo.connect(
            dojo.byId('url'), 'onkeypress', function (e) {
                if (e.keyCode == 13)
                    web_frame_application.enter(dijit.byId('url').getValue());
            });

        dojo.forEach(
            urls, function (src) {
                var item = new dijit.MenuItem(
                    {
                        label: src,
                        onClick: function () {
                            web_frame_application.play_url(src);
                        }
                    }
                );
                dijit.byId("url_menu").addChild(item);
                web_frame_application.menu_items[src] = item;
            });
    });
