Ext.ns('z3c.formext.form');

(function(){

var mod = z3c.formext.form;

mod.Z3CFormPanel = Ext.extend(
  Ext.FormPanel,
  {
    initComponent: function(){
      this.items = [
        {
          xtype: 'panel',
          hidden: true,
          cls: 'x-form-invalid-msg',
          id: this.id+'-errors'
        }].concat(this.items || []);

      if (this.buttons){
        for (var i=0; i < this.buttons.length; i++){
          var button = this.buttons[i];
          if (typeof button.handler === 'object'){
            var thisForm = this;
            //damn, we have to do a copy.  hopefully a shallow copy is good enough.
            button.handlerConfig = {};
            for (var prop in button.handler){
              button.handlerConfig[prop] = button.handler[prop];
            }
            if (typeof button.handlerConfig.success === 'string'){
              button.handlerConfig.success = this.handlers[button.handlerConfig.success];
            }
            if (typeof button.handlerConfig.failure === 'string'){
              button.handlerConfig.failure = this.handlers[button.handlerConfig.failure];
            }
            Ext.applyIf(
              button.handlerConfig,
              {
                url: this.ajaxHandlers[button.id],
                failure: this.handleErrors,
                success: function(){}
              });
            button.handler = function(){
              this.handlerConfig.method = thisForm.getForm().getValues(true) ? 'POST':'GET';
              thisForm.getForm().doAction(
                'submit',
                this.handlerConfig
              );
            };
          }
        }

      }
      mod.Z3CFormPanel.superclass.initComponent.call(this);
    },

    afterRender: function(){
      mod.Z3CFormPanel.superclass.afterRender.call(this);
      this.getForm().items.each(
        function(field){
          if (field.title){
            field.on(
              'render',
              function(){
                Ext.QuickTips.register(
                  {
                    target: this.getEl(),
                    text: this.title
                  });

              }, field, {single:true});
          }
        });
    },

    handleErrors: function(form, action){
      var errors = Ext.getCmp(this.id+'-errors');
      if (errors) {
        errors.getEl().update(action.result.formErrors.join('\n'));
        errors.show();
      }
    }
  });
Ext.reg('z3c-formpanel', mod.Z3CFormPanel);

})();
