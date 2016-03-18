from events import *
from model import *
from eventmanager import EventManager
from sjbeasts import PygameMasterController, CPUSpinnerController, PygameMasterView
from network import *
import network

from twisted.spread import pb

#------------------------------------------------------------------------------
class NetworkServerView(pb.Root):
	"""We SEND events to the server through this object"""
	STATE_PREPARING = 0
	STATE_CONNECTING = 1
	STATE_CONNECTED = 2

	#----------------------------------------------------------------------
	def __init__(self, evManager, sharedObjectRegistry, clientController):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.state = NetworkServerView.STATE_PREPARING
		self.server = None

		self.sharedObjs = sharedObjectRegistry
		self.clientController = clientController

	#----------------------------------------------------------------------
	def Connected(self, server):
		print "CONNECTED"
		self.server = server
		self.state = NetworkServerView.STATE_CONNECTED
		ev = ServerConnectEvent( server )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def ConnectFailed(self, server):
		self.state = NetworkServerView.STATE_PREPARING
		print "CONNECTION FAILED"

	#----------------------------------------------------------------------
	def Notify(self, event):
		ev = event
		#if isinstance( event, FlipCardRequest):
			#print "888888888888888888888888"

		if isinstance( event, TickEvent ) \
		   and self.state == NetworkServerView.STATE_PREPARING:
			self.state = NetworkServerView.STATE_CONNECTING

			#remoteResponse = pb.getObjectAt("localhost", 8000, 30)
			remoteResponse = pb.connect("localhost", 8000, 
			                            "user1", "asdf",
			                            "myService", "perspective1",
			                            timeout=30)

			remoteResponse.addCallback(self.Connected )
			#errback                  #self.ConnectFailed)

		#see if it's Copyable.  If not, see if there's a Copyable 
		#replacement for it.  If not, just ignore it.
		if not isinstance( event, pb.Copyable):
			evName = event.__class__.__name__
			if not hasattr( network, "Copyable" + evName ):
				return
			copyableClass = getattr( network, "Copyable" + evName )
			if copyableClass not in clientToServerEvents:
				return
			ev = copyableClass( event, self.sharedObjs )

		elif ev.__class__ not in clientToServerEvents:
			print "CLIENT NOT SENDING: " +str(ev)
			return 
			
		print "<== Sending to server:", ev.name
		remoteCall = self.server.callRemote("ClientEvent",ev,
		                                    self.clientController) 




#------------------------------------------------------------------------------
class NetworkServerController(pb.Referenceable):
	"""We RECEIVE events from the server through this object"""
	def __init__(self, evManager, twistedReactor):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.reactor = twistedReactor

		#we need to keep the events in order, so we track the active
		#event, and keep an event Queue.
		self.activeEventClass = None
		self.eventQueue = []

	#----------------------------------------------------------------------
	def remote_ServerEvent(self, event):
		#print "=================GOT AN EVENT FROM SERVER:", str(event)
		self.eventQueue.append( event )

		if self.activeEventClass is None:
			self.DequeueNextEvent()

		return 1

	#----------------------------------------------------------------------
	def DequeueNextEvent( self ):
		if not self.eventQueue:
			return
		if self.activeEventClass is not None:
			print "WEIRD.  activeEventClass is not None"

		event = self.eventQueue.pop(0)
		
		evClass = None
		import events
		#does the events module have an event with the same name
		if hasattr( events, event.name ):
			evClass = getattr( events, event.name )

		#does the events module have an event named the same,
		#except without 'Copyable' at the front?
		evName = event.__class__.__name__.replace('Copyable','',1)
		print "watching for", evName
		if hasattr(events, evName):
			evClass = getattr( events, evName )

		if evClass is None:
			print "Couldn't get event class to watch for"

		self.activeEventClass = evClass

		self.evManager.Post( event )

	#----------------------------------------------------------------------
	def remote_Ping(self):
		pong = 1
		return pong

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, ServerConnectEvent ):
			print "DO I GET IN HERE?"
			#tell the server that we're listening to it and
			#it can access this object
			remoteResponse = event.server.callRemote(
			                                       "ClientConnect", 
			                                       self )
		if isinstance( event, TickEvent ):
			#print "PUMPING NETWORK"
			self.reactor.iterate()

		if self.activeEventClass \
		  and isinstance( event, self.activeEventClass ):
		  	self.activeEventClass = None
			if self.eventQueue:
				self.DequeueNextEvent()


#------------------------------------------------------------------------------
class PhonyEventManager(EventManager):
	"""this object is responsible for coordinating most communication
	between the Model, View, and Controller."""
	#----------------------------------------------------------------------
	def Notify( self, event ):
		print "PHONY gets", event
		pass
	def Debug(self, ev):
		#return
		if isinstance( ev, GUIFocusThisWidgetEvent ):
			return
		if not isinstance( ev, GUIMouseMoveEvent ):
			#print "self", self
			print "  Phony   Message: " + ev.name

#------------------------------------------------------------------------------
class PhonyModel:
	"""..."""
	#----------------------------------------------------------------------
	def __init__(self, evManager, sharedObjectRegistry):
		self.sharedObjs = sharedObjectRegistry
		self.game = None
		self.server = None
		self.phonyEvManager = PhonyEventManager()
		self.realEvManager = evManager
		print "REAL", self.realEvManager
		print "FAKE", self.phonyEvManager
		self.neededObjects = [] 
		self.waitingObjectStack = []

		self.realEvManager.RegisterListener( self )

	#----------------------------------------------------------------------
 	def GameReturned(self, response):
		if response[0] == 0:
			print "GameReturned : game HASNT started"
			#the game has not been started on the server.
			#we'll be informed of the gameID when we receive the
			#GameStartedEvent
			return None
		else:
			gameID = response[0]
			print "GameReturned : game started ", gameID

			self.sharedObjs[gameID] = self.game
		return self.ObjStateReturned( response, self.GameSyncCallback )

	#----------------------------------------------------------------------
	def ReplacePlaceholder( self, obj, objID ):
		"""Call this when setCopyableState returns successfully"""
		#if it was just a Placeholder object, get the real
		#object and change the registry accordingly
		if isinstance( obj, Placeholder ):
			obj = obj.ChangeToFullObject()
			if obj is None:
				print "This should never happen"
				raise Exception("Placeholder finish")
			#import gc
			#refs = gc.get_referrers( self.sharedObjs[objID] )
			#if refs:
				#print "about to replace placeholder",
				#print self.sharedObjs[objID], ", but"
				#print "these objects still refer to it"
				#from pprint import pprint
				#pprint( refs )
			#self.sharedObjs[objID] = obj
			#TODO: what about all the other objects that used to
			# point to self.sharedObjs[objID]?  shouldn't their
			# references be replaced?

	#----------------------------------------------------------------------
 	def ObjStateReturned(self, response, nextFn=None):
		"""this is a callback that is called in response to 
		invoking GetObjectState on the server"""
		"""This will recursively grab all objects needed by eventually
		calling GetAllNeededObjects"""

		objID = response[0]
		objDict = response[1]

		print "looking for ", response
		if response[1] == 0:
			print "GOT ZERO -- better error handler here"
			print "Failed on key", objID
			print "corresponds to obj:", self.sharedObjs[objID]
			return None

		obj = self.sharedObjs[objID]

		if obj is None:
			print objID
			print self.sharedObjs
		retval = obj.setCopyableState(objDict, self.sharedObjs)
		if retval[0] == 1:
			#we successfully set the state and no further objects
			#are needed to complete the current object
			if objID in self.neededObjects:
				self.neededObjects.remove(objID)

			#self.ReplacePlaceholder( obj, objID )

		else:
			#to complete the current object, we need to grab the
			#state from some more objects on the server.  The IDs
			#for those needed objects were passed back in retval[1]
			for neededObjID in retval[1]:
				if neededObjID not in self.neededObjects:
					self.neededObjects.append(neededObjID)
			print "failed.  still need ", self.neededObjects

		#First check to see if this object is already in the 
		#waitingObjectStack, if not, append it.
		#(this is a List Comprehension, might be unfamiliar to newbies)
		if objID not in [item[1] for item in self.waitingObjectStack]:
			self.waitingObjectStack.append( 
			                        (obj, objID, objDict, nextFn)
			                              )

		self.GetAllNeededObjects()
	

	#----------------------------------------------------------------------
 	def GetAllNeededObjects(self):
		if len(self.neededObjects) == 0:
			#this is the recursion-ending condition.  If there are
			#no more objects needed to be grabbed from the server
			#then we can try to setCopyableState on them again and
			#we should now have all the needed objects, ensuring
			#that setCopyableState succeeds
			print "Got all objs.  realize.  Waiting Objs:"
			print self.waitingObjectStack, "\n--***---"
			while self.waitingObjectStack:
				t = self.waitingObjectStack.pop()
				obj = t[0]
				objID = t[1]
				objDict = t[2]
				fn = t[3]
				print "popped", obj.__class__.__name__
				retval = obj.setCopyableState(objDict, self.sharedObjs)
				if retval[0] == 0:
					print "WEIRD!!!!!!!!!!!!!!!!!!",
					print obj.__class__, "returned 0"
				elif retval[0] == 1:
					self.ReplacePlaceholder( obj, objID )

				print "fn is ", fn
				if fn:
					fn( obj )
					#from pprint import pprint
					#pprint( self.sharedObjs )
			return

		#still in the recursion step.  Try to get the object state for
		#the objectID on the end of the stack.  Note that the recursion
		#is done via a deferred, which may be confusing 
		nextID = self.neededObjects[len(self.neededObjects)-1]
		print "--"
		print "grabbing from server: ", nextID
		remoteResponse= self.server.callRemote("GetObjectState", nextID)
		remoteResponse.addCallback(self.ObjStateReturned)
		
	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, ServerConnectEvent ):
			self.server = event.server
			#when we connect to the server, we should get the
			#entire game state.  this also applies to RE-connecting
			if not self.game:
				self.game = Game( self.phonyEvManager )
			remoteResponse = self.server.callRemote("GetGame")
			remoteResponse.addCallback(self.GameReturned)

		elif isinstance( event, CopyableGameStartedEvent ):
			gameID = event.gameID
			if not self.game:
				self.game = Game( self.phonyEvManager )
			self.sharedObjs[gameID] = self.game
			ev = GameStartedEvent( self.game )
			self.realEvManager.Post( ev )

		elif hasattr( event, 'ReformatLocalToClient' ):
			print "==> Got from server:", event.name
			ev = event.ReformatLocalToClient( self.sharedObjs )
			if ev:
				self.realEvManager.Post( ev )
			else:
				event.ClientFetchNeededRemoteObjects( self )



		#=== Here is some stuff to get it working for now
		#=== TODO: make these work for real
		if isinstance( event, PlayerExploreRequest ):
			self.phonyEvManager.Post( event )

	#----------------------------------------------------------------------
	def ReformattingCallback( self, ev ):
		self.realEvManager.Post( ev )
		
	#----------------------------------------------------------------------
 	def GameSyncCallback(self, game):
		print "sending out the GS EVENT------------------==========="
		ev = GameSyncEvent( game )
		self.realEvManager.Post( ev )


#------------------------------------------------------------------------------
def main():
	"""..."""
	evManager = EventManager()
	sharedObjectRegistry = {}

	#import random
	#rng = random.Random()
	#clientID = rng.randrange( 1, 10000 )
	#playerName = str( rng.randrange(1,100) )
	#player = Player( evManager )

	from sjbeasts import AnimationTimerController
	keybd = PygameMasterController( evManager )
	spinner = CPUSpinnerController( evManager )
	animationSpinner = AnimationTimerController( evManager )
	pygameView = PygameMasterView( evManager )

	phonyModel = PhonyModel( evManager, sharedObjectRegistry  )

	import gui
	gui.playerRef = gui.GlobalPlayer( evManager )
	print gui.playerRef

	#from twisted.spread.jelly import globalSecurity
	#globalSecurity.allowModules( network )

	from twisted.internet import reactor
	serverController = NetworkServerController( evManager, reactor )
	serverView = NetworkServerView( evManager, sharedObjectRegistry, serverController )
	
	spinner.Run()

if __name__ == "__main__":
	main()
