z3c.formext.ModuleLoader.load(
  'z3c.formext.form',
  function(){
    if (config.ownerCt){
      var container = Ext.getCmp(config.ownerCt);
      delete config.ownerCt;
      container.add(new z3c.formext.form.Z3CFormPanel(config));
      container.doLayout();
    } else if (config.renderTo){
      new z3c.formext.form.Z3CFormPanel(config);
    }
  });