

class z3c.reference.imagetool.core.EventInfo {
	
	private var broadcaster:Object;
	private var event:String
	private var info:Object;

	public function EventInfo(bc:Object,eventName:String) {
		broadcaster = bc;
		event = eventName;
		info = new Object();
	}
	
    /**
        @return a pointer to the object which has fired 
        the event. there is no type-specification of the 
        broadcaster, because it can be of any type.
    */
	public function getBroadcaster(Void){
		return broadcaster;
	}
	
	public function getEvent(Void):String {
		return event;
	}
	
	public function setEvent(val:String):Void {
		event=val;
	}
	
	public function setInfo(key:String,info_obj):Void {
		info[key] = info_obj;
	}
	
	public function getInfo(key:String) {
		return info[key];
	}
}