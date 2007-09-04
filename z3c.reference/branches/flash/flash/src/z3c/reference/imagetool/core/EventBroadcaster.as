import z3c.reference.imagetool.core.EventInfo;

class z3c.reference.imagetool.core.EventBroadcaster
{
	public var _listeners:Array;
    
	public function EventBroadcaster() {

		_listeners = new Array();
	}

	public function addListener(obj:Object,e:String):Void {
		
		var l = {target:obj, event:e};
		
		for (var i in _listeners) {
			if (_listeners[i].target == l.target &&
				_listeners[i].event == l.event) {
					// this listener is allready registered
					return;	
			}
		}
		
		_listeners.push(l);
	}
	
	public function removeListener(obj:Object,e:String):Void {
		
		var l = {target:obj, event:e};
		for (var i in _listeners) {
			if (_listeners[i].target == l.target &&
				_listeners[i].event == l.event) _listeners.splice(Number(i),1);
		}
	}
	
	public function clearListener(Void):Void {
		_listeners = new Array();
	}
	
	public function broadcastEvent(eventInfo:EventInfo) {
		for (var i in _listeners) {
			
			if (_listeners[i].event == eventInfo.getEvent() ||
				_listeners[i].event == null) {
				
				_listeners[i].target[eventInfo.getEvent()].call(_listeners[i].target,eventInfo)
			}
		}
	}   
	
	/**
		use this method for debugging only
	*/
	public function getListeners():Array{
		return _listeners;
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
}