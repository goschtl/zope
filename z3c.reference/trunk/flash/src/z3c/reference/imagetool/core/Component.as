import z3c.reference.imagetool.core.*;

class z3c.reference.imagetool.core.Component extends MovieClip implements z3c.reference.imagetool.core.IFEventBroadcaster {
	
	private var log_txt:TextField;
	private var _bc:EventBroadcaster;
	
	function Component() {
		super();
		_bc=new EventBroadcaster();
	}
	
	/**
        very simple log
    */
    private function log(msg, param2:Object, param3:Object):Void{
        
        //write into log_txt
		_root.log_txt.text+=msg+"\n";
        _root.log_txt.scroll = _root.log_txt.maxscroll;
		
        //clear the console on maxlength
        //if (_root.log_txt.maxscroll > 100) _root.log_txt.text="";
                        
		//trace it
		trace(msg)
		
		//pass it to the external alcon debug consol
		net.hiddenresource.util.debug.Debug.trace(msg, param2, param3);
    }

	private function alert(msg:Object):Void {
		
		getURL("JavaScript:alert('"+String(msg)+"');");
		
	}
	
	/** 
		event handling
	*/
	public function addListener(obj:Object,e:String):Void {
		_bc.addListener(obj, e);
	}
	public function removeListener(obj:Object,e:String):Void {
		_bc.removeListener(obj, e);
	}
	public function broadcastEvent(eventInfo:z3c.reference.imagetool.core.EventInfo):Void {
		_bc.broadcastEvent(eventInfo);
	}
	
	/**
		use this method for debugging only
	*/
	public function getListeners():Array{
		return _bc.getListeners();
	}
    
    
	
}