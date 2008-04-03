Ext.namespace('zc.extjs');

zc.extjs.util = function() {

    // Maybe connections are expensive. Who knows. They appear to want
    // to be reused.
    var server_connection = new Ext.data.Connection();

    function call_server (args)
    {
        var callback = function (options, success, response) {
            if (! success)
            {
                system_error(args.task);
                if (args.failure)
                    args.failure({});
            }
            else
            {
                result = eval("("+response.responseText+")");
                if (result.session_expired)
                    return session_expired();

                if (result.error)
                {
                    Ext.MessageBox.alert(args.task+' failed',
                                         result.error);
                    if (args.failure)
                        args.failure(result);
                }
                else
                {
                    if (args.success)
                        args.success(result);
                }
            }
        };

        if (args.jsonData)
        {
            server_connection.request({
                url: args.url, jsonData: args.jsonData, method: 'POST',
                callback: callback});
        }
        else
            server_connection.request({
                url: args.url, params: args.params,
                callback: callback});
    }

    function get_form_config(args)
    {
        var config = Ext.apply({}, args.config);

        if (config.buttons === undefined)
            config.buttons = [];

        if (config.items === undefined)
            config.items = [];

        for (var i=0; i < args.definition.widgets.length; i++)
            config.items.push(zc.extjs.widgets.Field(
                args.definition.widgets[i]));

        for (var i=0; i < args.definition.actions.length; i++) {
            var url = args.definition.actions[i].url;
            config.buttons.push({
                text: args.definition.actions[i].label,
                id: args.definition.actions[i].name,
                handler: function () {
                    var form = config.form;
                    if (! form_valid(form))
                        return;
                    form.getForm().submit({
                        url: url,
                        waitMsg: '...',
                        failure: zc.extjs.util.form_failure,
                        success: args.after
                    });
                }
            });
        }
        return config;
    }

    function new_form(args)
    {
        var config = get_form_config(args);
        var form = new Ext.form.FormPanel(config);
        config.form = form; // Used for action handlers (see get_form_config)
        return form;
    }

    function form_panel(args)
    {
        call_server({
            url: args.url,
            params: args.params,
            task: "Loading form definition",
            success: function (result) {
                var formpanel;
                var form_config = {
                    autoHeight: true,
                    buttons: [{
                        text: 'Cancel',
                        handler: function ()
                        {
                            form_reset(formpanel, result.data);
                        }
                    }]
                };

                if (args.form_config) {
                    if (args.form_config.buttons)
                        args.form_config.buttons = (
                            args.form_config.buttons.concat(
                                form_config.buttons));
                    form_config = Ext.apply(form_config, args.form_config);
                }

                formpanel = zc.extjs.util.new_form({
                    definition: result.definition,
                    config: form_config,
                    after: function (form, action)
                    {
                        if (args.after)
                            args.after(form, action);
                    }
                });

                form_reset(formpanel, result.data);
                args.callback(formpanel);
            }
        });
    }

    function form_dialog(args)
    {
        var dialog;
        return function (data) {
            if (dialog)
            {
                form_reset(dialog.initialConfig.items[0], data);
                return dialog.show();
            }
            call_server({
                url: args.url,
                params: args.params,
                task: "Loading form definition",
                success: function (result) {

                    var form_config = {
                        autoHeight: true,
                        buttons: [{
                            text: 'Cancel',
                            handler: function ()
                            {
                                dialog.hide();
                            }
                        }]
                    };
                    if (args.form_config)
                    {
                        if (args.form_config.buttons)
                            args.form_config.buttons = (
                                args.form_config.buttons.concat(
                                    form_config.buttons));
                        form_config = ext.apply(form_config, args.form_config);
                    }

                    var config = {
                        layout: 'fit',
                        modal: true,
                        autoHeight: true,
                        items: [
                            new_form({
                                definition: result.definition,
                                config: form_config,
                                after: function (form, action)
                                {
                                    dialog.hide();
                                    if (args.after)
                                        args.after(form, action);
                                }
                            })
                        ]
                    };
                    if (args.window_config)
                        config = Ext.apply(config, args.window_config);
                    if (result.definition.title)
                        config.title = result.definition.title;
                    dialog = new Ext.Window(config);
                    dialog.show();
                    
                    if (data)
                    {
                        if (result.data)
                            result.data = Ext.apply(result.data, data);
                        else
                            result.data = data;
                    }
                    form_reset(dialog.initialConfig.items[0], result.data);
                }
            });
        };
    }

    function form_failure (form, action)
    {
        if (action.result && action.result.session_expired)
            session_expired();
        else if (action.result && action.result.error)
            Ext.MessageBox.alert("Couldn't submit form", action.result.error);
        else if (! (action.result && action.result.errors))
            system_error("Submitting this form");
    }

    function form_reset(formpanel, data)
    {
        formpanel.getForm().reset();
        if (data)
            for (var field_name in data)
                formpanel.find('name', field_name)[0].setValue(
                    data[field_name]);
    }

    function form_valid(form) 
    {
        if (form.getForm().isValid())
            return true;
        Ext.MessageBox.alert('Errors', 'Please fix the errors noted.');
        return false;
    }

    function init()
    {
        Ext.QuickTips.init();
    }

    function map(func, sequence)
    {
        var result = [];
        for (var i=0; i < sequence.length; i++)
            result.push(func(sequence[i]));
        return result;
    }

    function session_expired()
    {
        Ext.MessageBox.alert(
            'Session Expired',
            "You will need to log-in again.",
            window.location.reload.createDelegate(window.location)
        );
    }

    function system_error(task)
    {
        Ext.MessageBox.alert("Failed",task+" failed for an unknown reason");
    }

    return {
        call_server: call_server,
        new_form: new_form,
        form_dialog: form_dialog,
        form_panel: form_panel,
        form_failure: form_failure,
        form_reset: form_reset,
        form_valid: form_valid,
        init: init,
        map: map,
        system_error: system_error
    };
}();

Ext.form.Field.prototype.msgTarget = 'under';
Ext.onReady(zc.extjs.util.init);
