
interface z3c.reference.imagetool.core.IFEventBroadcaster{
	
	public function addListener(obj:Object,e:String):Void;
	public function removeListener(obj:Object,e:String):Void;
	public function broadcastEvent(eventInfo:z3c.reference.imagetool.core.EventInfo):Void;

}