# -*- Mode: Python; tab-width: 4 -*-

import asyncore
import asynchat

import os
import socket
import string
import thread
	
class trigger (asyncore.dispatcher):

	"Wake up a call to select() running in the main thread"

	# This is useful in a context where you are using Medusa's I/O
	# subsystem to deliver data, but the data is generated by another
	# thread.  Normally, if Medusa is in the middle of a call to
	# select(), new output data generated by another thread will have
	# to sit until the call to select() either times out or returns.
	# If the trigger is 'pulled' by another thread, it should immediately
	# generate a READ event on the trigger object, which will force the
	# select() invocation to return.

	# A common use for this facility: letting Medusa manage I/O for a
	# large number of connections; but routing each request through a
	# thread chosen from a fixed-size thread pool.  When a thread is
	# acquired, a transaction is performed, but output data is
	# accumulated into buffers that will be emptied more efficiently
	# by Medusa. [picture a server that can process database queries
	# rapidly, but doesn't want to tie up threads waiting to send data
	# to low-bandwidth connections]

	# The other major feature provided by this class is the ability to
	# move work back into the main thread: if you call pull_trigger()
	# with a thunk argument, when select() wakes up and receives the
	# event it will call your thunk from within that thread.  The main
	# purpose of this is to remove the need to wrap thread locks around
	# Medusa's data structures, which normally do not need them.  [To see
	# why this is true, imagine this scenario: A thread tries to push some
	# new data onto a channel's outgoing data queue at the same time that
	# the main thread is trying to remove some]

	def __init__ (self):

		# Although SOCK_DGRAM => UDP => unreliable, this should not be
		# the case for AF_UNIX sockets, or for sockets bound to a
		# loopback interface.
		if os.name == 'posix':
			addr = '/tmp/.select-trigger.%d' % os.getpid()
			family = socket.AF_UNIX
		else:
			addr = ('127.4.4.4', 44444)
			family = socket.AF_INET

		# non-blocking socket, read from by medusa
		self.create_socket (family, socket.SOCK_DGRAM)
		# 'blocking' socket, written to by child threads.
		self.trigger = socket.socket (family, socket.SOCK_DGRAM)

		self.bind (addr)
		self.lock = thread.allocate_lock()
		self.thunks = []
		
	def readable (self):
		return 1

	def writable (self):
		return 0

	def pull_trigger (self, thunk=None):
		if thunk:
			try:
				self.lock.acquire()
				self.thunks.append (thunk)
			finally:
				self.lock.release()					
			msg = str(id(thunk))
		else:
			msg = 'Bang!'
		self.trigger.sendto (msg, self.addr)

	def handle_connect(self): pass

	def handle_read (self):
		what, where = self.recvfrom (128)
		if what != 'Bang!':
			thunk_id = int (what)
			for thunk in self.thunks:
				if id(thunk) == thunk_id:
					try:
						self.lock.acquire()
						self.thunks.remove(thunk)
					finally:
						self.lock.release()
					thunk()
					thunk_id = 0
			if thunk_id:
				print 'Warning: Lost Thunk! (id=%x)' % thunk_id

class trigger_file:

	"A 'triggered' file object"

	def __init__ (self, trigger, parent):
		self.trigger = trigger
		self.parent = parent
		
	def write (self, data):
		self.trigger.pull_trigger (
			lambda d=data,s=self: s.parent.push (d)
			)

	def writeline (self, line):
		self.write (line+'\r\n')
		
	def writelines (self, lines):
		self.write (
			string.joinfields (
				lines,
				'\r\n'
				) + '\r\n'
			)

	def flush (self):
		pass

	def softspace (self, *args):
		pass

	def close (self):
		# You might have the do a self.parent.push (None)
		# in a derived class.
		pass

if __name__ == '__main__':
	
	import time

	the_trigger = trigger()

	def thread_function (output_file, i, n):
		print 'entering thread_function'
		while n:
			time.sleep (5)
			output_file.write ('%2d.%2d %s\r\n' % (i, n, output_file))
			output_file.flush()
			n = n - 1
		output_file.close()
		print 'exiting thread_function'

	class thread_parent (asynchat.async_chat):
		
		def __init__ (self, conn, addr):
			self.addr = addr
			asynchat.async_chat.__init__ (self, conn)
			self.set_terminator ('\r\n')
			self.buffer = ''
			self.count = 0

		def collect_incoming_data (self, data):
			self.buffer = self.buffer + data

		def found_terminator (self):
			data, self.buffer = self.buffer, ''
			n = string.atoi (string.split (data)[0])
			tf = trigger_file (the_trigger, self)
			self.count = self.count + 1
			thread.start_new_thread (thread_function, (tf, self.count, n))

	class thread_server (asyncore.dispatcher):

		def __init__ (self, family=socket.AF_INET, address=('', 9003)):
			asyncore.dispatcher.__init__ (self)
			self.create_socket (family, socket.SOCK_STREAM)
			self.set_reuse_addr()
			self.bind (address)
			self.listen (5)

		def handle_accept (self):
			conn, addr = self.accept()
			tp = thread_parent (conn, addr)

	thread_server()
	#asyncore.loop(1.0, use_poll=1)
	asyncore.loop ()
