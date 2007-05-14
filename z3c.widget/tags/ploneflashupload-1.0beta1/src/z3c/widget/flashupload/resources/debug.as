/*
  this small script allows you to see the log if you press
  SHIFT + F12

  very nice for debugging :)
 */
_root.listener = new Object();
_root.listener.onKeyUp = function(){
	trace(Key.getCode());
	if (Key.getCode() == 123 && Key.isDown(Key.SHIFT)){

        _root.debug_txt._visible = !_root.debug_txt._visible;
		
		_root.debug_txt._x = 0;
		_root.debug_txt._y = 0;
		_root.debug_txt._width = Stage.width - 1;
		_root.debug_txt._height = Stage.height - 1;
	}
	
}
Key.addListener(_root.listener);

_root.debug_txt._visible = false;