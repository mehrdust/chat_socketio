from bottle import Bottle, request
from socketio import server, namespace, socketio_manage
from mixins import RoomsMixin, BroadcastMixin

app = Bottle()

class ChatService(namespace.BaseNamespace, RoomsMixin, BroadcastMixin):
	nicknames = []
	def initialize(self):
		print "inside initialize"
		print self.socket

	def on_hello(self, data):
		print "hello", data
		self.emit('greetings', {'from': 'sockets'})
	
	""" triggers when the user joins the room """	
	def on_join(self, room):
		print self.socket.session
		print "Joined room: " + room
		print "============="
		self.room = room
		self.join(room)
		print self.socket.session
		print "Joined room: " + room
		print "============="
		return True

	""" is triggered when the user nickname is passed to service """
	def on_nickname(self, nickname):
		print self.socket.session
		print "============="
		print 'Nickname: {0}'.format(nickname)
		self.nicknames.append(nickname)
		self.socket.session['nickname'] = nickname
		self.broadcast_event('announcement', '%s has connected' % nickname)
		self.broadcast_event('nicknames', self.nicknames)
		return True, nickname

	""" is triggered when a message is received """    	
	def on_user_message(self, msg):
		print self.socket.session
		print "============="
		print 'User message: {0}'.format(msg)
		self.emit_to_room(self.room, 'msg_to_room',
			self.socket.session['nickname'], msg)
		return True

	def on_disconnect(self, room):
		print self.socket.session
		print "============="
		# Remove nickname from the list.
		print 'Disconnected'
		nickname = self.socket.session['nickname']
		self.nicknames.remove(nickname)
		self.broadcast_event('announcement', '%s has disconnected' % nickname)
		self.broadcast_event('nicknames', self.nicknames)
		self.disconnect(silent=True)
		return True


	def recv_disconnect(self):
		print self.socket.session
		print "============="
		# Remove nickname from the list.
		print 'Disconnected'
		nickname = self.socket.session['nickname']
		self.nicknames.remove(nickname)
		self.broadcast_event('announcement', '%s has disconnected' % nickname)
		self.broadcast_event('nicknames', self.nicknames)
		self.disconnect(silent=True)
		return True


""" Here routing is taken care of """
@app.route('/socket.io/<arg:path>')
def socketio(*arg, **kw):
    socketio_manage(request.environ, {'': ChatService}, request=request)
    return "out"


if __name__ == '__main__':
	host = 'localhost'
	port = 9090
	print "======================================================="
	print "Chat service is started @ http://" + host + ":" + str(port)	
	print "======================================================="
	server.SocketIOServer(
		(host, port), app, policy_server=False).serve_forever()
