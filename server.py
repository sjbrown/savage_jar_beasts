#! /usr/bin/python

from model import *
from eventmanager import EventManager
from events import *
from network import *
import network

from twisted.spread import pb

#------------------------------------------------------------------------------
class TimerController:
	"""A controller that sends of an event every second"""
	def __init__(self, evManager, reactor):
		print "Timer created"
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.reactor = reactor
		self.numClients = 0

	#-----------------------------------------------------------------------
	def NotifyApplicationStarted( self ):
		self.reactor.callLater( 1, self.Tick )

	#-----------------------------------------------------------------------
	def Tick(self):
		if self.numClients == 0:
			return

		ev = SecondEvent()
		self.evManager.Post( ev )
		self.reactor.callLater( 1, self.Tick )

		self.evManager.Post( TickEvent() )

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, ClientConnectEvent ):
			self.numClients += 1
			if self.numClients == 1:
				self.Tick()
		if isinstance( event, ClientDisconnectEvent ) \
		  or isinstance( event, ExplicitClientDisconnectEvent ):
			self.numClients -= 1

#------------------------------------------------------------------------------
class NetworkClientController(pb.Perspective):
	"""We RECEIVE events from the CLIENT through this object"""
	def __init__(self, perspectiveName):
		self.perspectiveName = perspectiveName
		self.evManager = None

		self.sharedObjs = None

		self.pendingPlayerJoins = {}
		self.playersToClients = {}

		#this is needed for GetEntireState()
		self.game = None

	#----------------------------------------------------------------------
	def PostInit(self, evManager, sharedObjectRegistry):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.sharedObjs = sharedObjectRegistry

	#----------------------------------------------------------------------
	def detached(self, client, identity):
		print "Client ******DETACHED****** they were", identity
		for key,val in self.pendingPlayerJoins.iteritems():
			if val == client:
				del self.pendingPlayerJoins[key]

		for key,val in self.playersToClients.iteritems():
			if val == client:
				del self.playersToClients[key]

		ev = ExplicitClientDisconnectEvent( client )
		self.evManager.Post( ev )

		self.evManager.Post( TickEvent() )

	#----------------------------------------------------------------------
	def perspective_ClientConnect(self, netClient):
		print "perspective CLIENT CONNECT"
		ev = ClientConnectEvent( netClient)
		self.evManager.Post( ev )

		self.evManager.Post( TickEvent() )
		return 1

	#----------------------------------------------------------------------
	def perspective_GetGame(self):
		"""this is usually called when a client first connects or
		when they had dropped and reconnect"""
		if self.game == None:
			return [0,0]
		gameID = id( self.game )
		gameDict = self.game.getStateToCopy( self.sharedObjs )

		self.evManager.Post( TickEvent() )
		print "returning: ", gameID
		return [gameID, gameDict]
	
	#----------------------------------------------------------------------
	def perspective_GetObjectState(self, objectID):
		#print "request for object state", objectID
		if not self.sharedObjs.has_key( objectID ):
			print "\nCLIENT ERR\tNo key on the server"
			print "Requested Key: ", objectID, "\n"
			return [objectID,0]
		object = self.sharedObjs[objectID]
		objDict = object.getStateToCopy( self.sharedObjs )

		self.evManager.Post( TickEvent() )
		return [objectID, objDict]
	
	#----------------------------------------------------------------------
	def perspective_ClientEvent(self, event, client):
		ev = event
		player = None
		if isinstance(event, PlayerJoinRequest):
			self.pendingPlayerJoins[event.playerDict['name']] = \
			                                                client
			ev = event
		elif hasattr( event, 'ReformatLocalToServer' ):
			print "reformatting..."
			ev = event.ReformatLocalToServer( self.sharedObjs )
		#elif isinstance(event, CopyableCharactorMoveRequest ):
			#print "reformatting..."
			#player = self.sharedObjs[event.playerID]
			#charactor = self.sharedObjs[event.charactorID]
			#direction = event.direction
			#ev = CharactorMoveRequest(player, charactor, direction)
		else:
			ev = event


		if player and self.playersToClients[player.name] != client:
			ev = PlayerClientMismatchEvent( player.name )

		self.evManager.Post( ev )

		self.evManager.Post( TickEvent() )
		return 1

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, GameStartedEvent ):
			self.game = event.game
		elif isinstance( event, PlayerJoinEvent ):
			pName = event.player.name
			if self.pendingPlayerJoins.has_key(pName):
				client = self.pendingPlayerJoins[pName]
				self.playersToClients[pName] = client
				del self.pendingPlayerJoins[pName]


#------------------------------------------------------------------------------
class NetworkClientView:
	"""We SEND events to the CLIENT through this object"""
	def __init__(self, evManager, sharedObjectRegistry):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.clients = []
		self.sharedObjs = sharedObjectRegistry
		#NOTE: this is no longer used.  see below in Notify()
		#every 5 seconds, the server should poll the clients to see if
		# they're still connected
		#self.pollSeconds = 0


	#----------------------------------------------------------------------
 	def Pong(self ):
		pass
	#----------------------------------------------------------------------
 	def RemoteCallError(self, failure, client):
		from twisted.internet.error import ConnectionLost
		#trap ensures that the rest will happen only 
		#if the failure was ConnectionLost
		failure.trap(ConnectionLost)
		self.DisconnectClient(client)
		return failure

	#----------------------------------------------------------------------
	def DisconnectClient(self, client):
		print "Disconnecting Client", client
		try:
			self.clients.remove( client )
		except ValueError:
			#Probably a harmless instance of trying to remove a
			#client twice
			pass
		ev = ClientDisconnectEvent( client ) #client id in here
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def RemoteCall( self, client, fnName, *args):
		from twisted.spread.pb import DeadReferenceError

		try:
			remoteCall = client.callRemote(fnName, *args)
			#remoteCall.addCallback( self.Pong )
			remoteCall.addErrback( self.RemoteCallError, client )
		except DeadReferenceError:
			self.DisconnectClient(client)


	#----------------------------------------------------------------------
 	def Notify(self, event):

		if isinstance( event, ClientConnectEvent ):
			self.clients.append( event.client )
			#TODO tell the client what it's ID is

		if isinstance( event, ExplicitClientDisconnectEvent ):
			self.DisconnectClient(event.client)

		# this would only be needed if we needed to timeout the clients
		# since we've got the handy ExplicitClientDisconnect, we don't
		# have to worry about it.  But still keep it here for reference
		#if isinstance( event, SecondEvent ):
			#self.pollSeconds +=1
			#if self.pollSeconds == 10:
				#self.pollSeconds = 0
				#for client in self.clients:
					#self.RemoteCall( client, "Ping" )


		ev = event

		#don't broadcast events that aren't Copyable
		if not isinstance( ev, pb.Copyable ):
			evName = ev.__class__.__name__
			if not hasattr( network, "Copyable"+evName):
				return
			copyableClass = getattr( network, "Copyable"+evName)
			if copyableClass not in serverToClientEvents:
				return
			ev = copyableClass( ev, self.sharedObjs )

		elif ev.__class__ not in serverToClientEvents:
			#print "SERVER NOT SENDING: " +str(ev)
			return 

		#NOTE: this is very "chatty".  We could restrict 
		#      the number of clients notified in the future
		for client in self.clients:
			print "==============server===sending: ", str(ev)
			self.RemoteCall( client, "ServerEvent", ev )
			if isinstance( ev, network.CopyableDuelStartEvent ):
				print "DuelID", ev.__dict__


#------------------------------------------------------------------------------
class TextLogView:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		#if isinstance( event, CharactorPlaceEvent ):
			#print event.name, " at ", event.charactor.sector

		#elif isinstance( event, CharactorMoveEvent ):
			#print event.name, " to ", event.charactor.sector

		if not isinstance( event, TickEvent ):
			print event.name

		


#------------------------------------------------------------------------------
def main():
	"""..."""
	from twisted.spread import pb
	from twisted.application import service
	from twisted.cred.authorizer import DefaultAuthorizer
	from twisted.internet import reactor,app

	evManager = EventManager()
	sharedObjectRegistry = {}

	log = TextLogView( evManager )
	timer = TimerController( evManager, reactor )
	#clientContr = NetworkClientController( evManager, sharedObjectRegistry )
	clientView = NetworkClientView( evManager, sharedObjectRegistry )
	game = Game( evManager )
	
	#from twisted.spread.jelly import globalSecurity
	#globalSecurity.allowModules( network )

	application = app.Application("myServer")
	auth = DefaultAuthorizer( application )

	#create a service, tell it to generate NetworkClientControllers
	serv = pb.Service( "myService", application, auth )
	serv.perspectiveClass = NetworkClientController

	#create a Perspective
	per1 = serv.createPerspective( "perspective1" )
	per1.PostInit( evManager, sharedObjectRegistry)

	#create an Identity
	iden1 = auth.createIdentity("user1")
	iden1.setPassword( "asdf" )
	#allow it access to the perspective named perspective1
	iden1.addKeyByString( "myService", "perspective1" )
	auth.addIdentity( iden1 )

	#application.listenTCP(8000, pb.BrokerFactory(clientContr) )
	application.listenTCP(8000, pb.PBServerFactory(pb.AuthRoot(auth)) )

	application.run(save=0)

if __name__ == "__main__":
	main()
