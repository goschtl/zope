//see http://extjs.com/forum/showthread.php?t=34808
/**
 * Javascript ResourceManager definition inc preloaders
 * @author Adam J Benson
 * @todo Add in the CSS on demand loaders
 * @version 1.3.1
 *
 * EXAMPLE PACKAGE DEFINITION: (All packages should be defined prior to trying to load them)
 *
 * var pack={
 *    name: "ExamplePack",
 *    description:"This is an example 'package object' which is used by the resource managers",
 *    scripts:["url1","url2","url3","url4"],
 *    callback: function(){},
 *    requires:["packageName"] //Dependancies for this package to be loaded before it...
 * }
 *
 * EXAMPLE USAGE (with callback)
 * ScriptManager('Common', function(){
 *   //YOUR CODE HERE
 *   var simple = new Ext.FormPanel();
 * });
 *
 * EXAMPLE USAGE (without callback)
 * ScriptManager('Common');
 *
 */
Ext.ns('z3c.formext');

var ScriptManager = window.ScriptManager = function( packageName, callback ) {
  /**
   * Constructor
   */
  ScriptManager.load(packageName,callback);
};

z3c.formext.ModuleLoader = ScriptManager;

ScriptManager.prototype = {
  registeredPackages:[], //List of packages that have been registered
  loadQueue:[], //Queue of packages that have been requested to load (we load sequentially to avoid dependancy issues)
  processing: false,

  register: function(packageConfig){
    //Register the package for loading
    this.registeredPackages[packageConfig.name]=packageConfig;
    this.registeredPackages[packageConfig.name].loaded=false;
  },

  load: function(packageName, callback) {
    /**
     * Load the specified package, with an optional callback (in addition to the callback configured by the packages config)
     */
    if(!this.registeredPackages[packageName]){
      //Package Not Found
      if (console && console.log){
        console.log("The package "+packageName+" has not been registered but was requested by a script.");
      }
      return;
    }
    if(this.registeredPackages[packageName].loaded==true){
      //Already loaded... Trigger the scripted callback
      ScriptManager.prototype.nextQueueItem();
      if(callback)callback.call();
      return;
    }
    if(this.registeredPackages[packageName].requires){
      //Required Scripts
      var required=this.registeredPackages[packageName].requires;
      for(var i=0, m=required.length; i < m;i++){
        if(this.registeredPackages[required[i]].loaded!=true){
          //There is a dependant not loaded, so add self to the queue and load it instead...

          /* the original author pushed the callback function onto the
          queue.  But then the callback would be called for each
          requirement being loaded.  Now we pass in an empty function
          as the call back so only the requested package's load does
          the callback */
          this.loadQueue.push([packageName,/*callback*/ function(){}]);
          this.load(required[i]);
        }
      }
    }
    if(ScriptManager.processing){
      //Already proccessing a script (or document body hasn't finished loading)! Add it to the queue...
      this.loadQueue.push([packageName,callback]);
      return;
    }
    ScriptManager.processing=true;
    ScriptManager.srcScript(this.registeredPackages[packageName], callback);
  },
  genScriptNode : function() {
    var scriptNode = document.createElement("script");
    scriptNode.setAttribute("type", "text/javascript");
    return scriptNode;
  },
  srcScript : function(packageConfig, callback) {
    var scriptNode = ScriptManager.prototype.genScriptNode();
    scriptNode.setAttribute("src", packageConfig.scripts[0]);
    scriptNode.onload = scriptNode.onreadystatechange = function() {
      if (!scriptNode.readyState || scriptNode.readyState == "loaded" || scriptNode.readyState == "complete" ||
          scriptNode.readyState == 4 && scriptNode.status == 200) {
        setTimeout(
          function(){
            ScriptManager.registeredPackages[packageConfig.name].loaded=true;
            ScriptManager.prototype.scriptLoaded();
            if(packageConfig.callback)packageConfig.callback.call();
            if(callback)callback.call();
          }, 200);
      }
    };
    var headNode = document.getElementsByTagName("head")[0];
    headNode.appendChild(scriptNode);
  },
  nextQueueItem : function(){
    if(this.loadQueue.length > 0){
      var currentItem=this.loadQueue.shift();
      ScriptManager.prototype.load(currentItem[0],currentItem[1]);
    }

  },
  scriptLoaded : function(){
    /**
     * Callback function for whenever a script finishes loading
     */
    ScriptManager.processing=false;
    ScriptManager.prototype.nextQueueItem();
  }

};
ScriptManager.register = ScriptManager.prototype.register;
ScriptManager.load = ScriptManager.prototype.load;
ScriptManager.loadQueue = ScriptManager.prototype.loadQueue;
ScriptManager.registeredPackages = ScriptManager.prototype.registeredPackages;
ScriptManager.srcScript = ScriptManager.prototype.srcScript;
ScriptManager.nextQueueItem=ScriptManager.prototype.nextQueueItem();