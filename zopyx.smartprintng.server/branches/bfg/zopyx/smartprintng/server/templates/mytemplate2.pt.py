registry = dict(version='3.7')
def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	def render(econtext, rcontext=None):
		macros = econtext.get('macros')
		_slots = econtext.get('_slots')
		target_language = econtext.get('target_language')
		u'_init_stream()'
		(_out, _write) = _init_stream()
		u'_init_tal()'
		(_attributes, repeat) = _init_tal()
		u'_init_default()'
		_default = _init_default()
		u'None'
		default = None
		u'None'
		_domain = None
		_write(u'<h1>hello world</h1>')
		return _out.getvalue()
	return render

registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
